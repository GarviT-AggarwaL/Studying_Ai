import os
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from groq import Groq
import re
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key not found!")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

#tools
def get_product_price(product):
    if product=="iphone-17":
        return 5000
    elif product=="iphone-15":
        return 500
    else:
        return 0
    
def calculator(expression):
    expression = expression.strip('"').strip("'")
    try:
        return eval(expression)
    except:
        return "calc error!"
    
tools = {
    "get_product_price":get_product_price,
    "calculator":calculator
}
    
system_prompt="""
You are shopping assistant.
You have these tools:
get_product_price(product)
calculator(expression)
IMPORTANT:
Call tools exactly like these examples:
Action: get_product_price("iphone-17")
Action: calculator("5000-1000")
never write:
get_product_price(product="iphone 17")
never write:
calculator(expression="5000-1000")
Follow these rules:
1. Decide what you need to do next.
2. Call only ONE tool at a time.
3. After writing an Action, STOP immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an observation.
6. Then decide your next action.
7. When the task is complete, give the final answer.

Format:

Thought: what you need to do
Action: tool_name(arguement)

When finished:
Final Answer: Your answer
""" 

def run_agent(question):
    messages = [{
        "role":"system",
        "content":system_prompt
    },
    {
        "role":"user",
        "content":question
    }]
    for step in range(5):

        print("\n-----------------")
        print("STEP",step+1)
        print("------------------")
        response=client.chat.completions.create(model="llama-3.3-70b-versatile",
                                            messages=messages,temperature=0)
        answer=response.choices[0].message.content
        print(answer)

    #Agent Has finished
        if"Final Answer:" in answer:
            break

    #find the Action
        match= re.search(
             r"Action:\s*([a-zA-Z_]\w*)\((.*?)\)",
             answer)
    
    
        if match:

            tool_name=match.group(1)
            tool_input=match.group(2)
            tool_input=tool_input.strip()
            tool_input=tool_input.strip("*")
            tool_input=tool_input.strip('"').strip("'")
        #Run the tool
        if tool_name in tools:
            tool=tools[tool_name]
            observation=tool(tool_input)
        else:
            observation="tool not found"

        print(
            "Observation:",
            observation
        )

        #add LLM response to memory
        messages.append({
            "role":"assistant",
            "content":answer
        })
        
        #Give tool result back to LLM
        messages.append({
            "role":"user",
            "content":
                "Observation: "
                 + str(observation)
        })
        sleep(5)

prompt="""
I have 5000 rupees. What is the price of an iphone-17?
and how much money will i have left?

"""
run_agent(prompt)