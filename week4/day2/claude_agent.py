
import os
import json
import ast
import operator
import math

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from your .env file")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing from your .env file")


# --------------------------------------------------
# 2. Initialize clients
# --------------------------------------------------

groq_client = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

MODEL = "openai/gpt-oss-120b"


# --------------------------------------------------
# 3. Web search tool
# --------------------------------------------------

def web_search(query: str) -> str:
    """Search the web using Tavily and return relevant results."""

    if not query.strip():
        return "Error: Search query cannot be empty."

    try:
        response = tavily_client.search(
            query=query,
            max_results=5
        )

        results = response.get("results", [])

        if not results:
            return "No relevant web results found."

        formatted_results = []

        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            })

        return json.dumps(
            formatted_results,
            ensure_ascii=False
        )

    except Exception as e:
        return f"Web search failed: {e}"


# --------------------------------------------------
# 4. Safe arithmetic calculator
# --------------------------------------------------

# Only these arithmetic operators are allowed.
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate_expression(node):
    """Evaluate an arithmetic expression without using eval()."""

    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Only numeric values are allowed.")

        if isinstance(node.value, int) and node.value.bit_length() > 1024:
            raise ValueError("Integer is too large.")

        if isinstance(node.value, float) and not math.isfinite(node.value):
            raise ValueError("Number must be finite.")

        return node.value

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in OPERATORS:
            raise ValueError("Unsupported arithmetic operator.")

        left = evaluate_expression(node.left)
        right = evaluate_expression(node.right)

        # Avoid excessively large exponent calculations.
        if isinstance(node.op, ast.Pow):
            if abs(right) > 1000:
                raise ValueError("Exponent is too large.")

            if abs(left) > 1 and right > 100:
                raise ValueError("Result would be too large.")

        result = OPERATORS[operator_type](left, right)

        if isinstance(result, int) and result.bit_length() > 4096:
            raise ValueError("Result is too large.")

        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result is not finite.")

        return result

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in OPERATORS:
            raise ValueError("Unsupported unary operator.")

        return OPERATORS[operator_type](
            evaluate_expression(node.operand)
        )

    raise ValueError(
        "Invalid expression. Use numbers and arithmetic operators only."
    )


def calculate(expression: str) -> str:
    """Calculate a basic arithmetic expression safely."""

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate_expression(tree.body)
        return str(result)

    except Exception as e:
        return f"Calculation error: {e}"


# --------------------------------------------------
# 5. Define tools in Groq's standard tool format
# --------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet for current information, facts, "
                "recent events, or information that requires web sources. "
                "Returns search results containing titles, URLs, and content."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to send to Tavily."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Calculate arithmetic expressions accurately. "
                "Use this tool for mathematical calculations instead of "
                "trying to calculate mentally. Supports +, -, *, /, //, %, "
                "**, parentheses, and unary + or -."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression, such as "
                            "'12345*12345' or '(10+5)*3'."
                        )
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    }
]


# --------------------------------------------------
# 6. Map tool names to Python functions
# --------------------------------------------------

available_functions = {
    "web_search": web_search,
    "calculate": calculate
}


# --------------------------------------------------
# 7. Main AI agent
# --------------------------------------------------

def run_agent(user_input: str) -> str:
    """Let the model choose tools, execute them, and answer."""

    if not user_input.strip():
        return "Please enter a query."

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant with access to two tools: "
                "web_search and calculate. Choose tools automatically when "
                "needed. Use calculate for arithmetic instead of mental "
                "calculation. Use web_search when current or source-based "
                "information is needed. You may call multiple tools if "
                "necessary. Base web-related claims on the returned results, "
                "and do not invent sources or calculations. After receiving "
                "tool results, provide a clear final answer."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    # Allow multiple rounds of tool calls.
    max_tool_rounds = 10

    for _ in range(max_tool_rounds):
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # If the model has finished, return its answer.
        if not message.tool_calls:
            return message.content or "The model returned no text answer."

        # Preserve the assistant's tool-call message in the conversation.
        messages.append(message)

        # Execute each requested tool and send back its result.
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )

                function_to_call = available_functions.get(
                    function_name
                )

                if function_to_call is None:
                    result = f"Unknown tool: {function_name}"
                else:
                    result = function_to_call(**arguments)

            except Exception as e:
                result = f"Tool execution error: {e}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    return "Stopped because the maximum number of tool rounds was reached."


# --------------------------------------------------
# 8. Take a string input and run the agent
# --------------------------------------------------

if __name__ == "__main__":
    user_query = input("Enter your query: ")

    try:
        answer = run_agent(user_query)
        print("\nAI Agent:", answer)

    except Exception as e:
        print(f"\nAgent error: {e}")
