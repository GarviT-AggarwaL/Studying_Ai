from __future__ import annotations
import os, random
from typing import Annotated, Literal, Optional, TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()
key = os.getenv("GROQ_API_KEY")
if not key:
    raise RuntimeError("Set GROQ_API_KEY in your .env file.")
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=key, temperature=0)
MENU = {"burger": 10, "pizza": 20, "momos": 4}
COOK_SUCCESS = 0.60
SERVE_SUCCESS = 0.60

class State(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    dish_name: str
    required_quantity: int
    available_quantity: str
    status: str
    order_retry_attempts: int
    cook_retry_attempts: int
    serve_retry_attempts: int
    final_result: bool
    retry_order_requested: bool
    partial_order_accepted: bool
    parsed_food_order: bool

class Extraction(BaseModel):
    is_food_order: bool = Field(description="Whether the user is trying to order food.")
    dish_name: Optional[str] = Field(default=None, description="One requested dish.")
    quantity: Optional[int] = Field(default=None, description="Positive integer; default to 1 if omitted.")
    reply: str = Field(description="Brief clarification or refusal for unrelated/unclear input.")

extract = llm.with_structured_output(Extraction)

def last_user_text(s: State) -> str:
    for m in reversed(s.get("messages", [])):
        if isinstance(m, HumanMessage):
            return str(m.content)
    return ""

def say(text: str) -> dict:
    return {"messages": [AIMessage(content=text)]}

def user_facing(prompt: str) -> str:
    r = llm.invoke([
        SystemMessage(content="You are a polite restaurant-ordering assistant. Keep replies brief. Never claim success unless told it succeeded."),
        HumanMessage(content=prompt),
    ])
    return str(r.content).strip()

def parse_order(s: State) -> dict:
    try:
        x = extract.invoke([
            SystemMessage(content=(
                "You are an intake parser for a restaurant ordering agent, not a general-purpose assistant. "
                "Only accept food-ordering requests. One dish per order. If quantity is omitted, use 1. "
                "Extract other food dishes too so the menu node can mark them unavailable. "
                "If unrelated, set is_food_order=false. If multiple different dishes or unclear input, "
                "return missing dish/quantity and ask for one dish and quantity. Normalize plural names if obvious."
            )),
            HumanMessage(content=last_user_text(s)),
        ])
    except Exception:
        return {**say("I couldn't read that order. Please enter one dish and quantity, e.g. '2 burgers'."),
                "status": "INVALID_INPUT", "parsed_food_order": False}
    if not x.is_food_order:
        return {**say("I'm a restaurant food-ordering AI agent. I can help order a dish and quantity, but can't answer general-purpose questions."),
                "status": "REJECTED", "parsed_food_order": False}
    if not x.dish_name or not x.dish_name.strip() or not x.quantity or x.quantity < 1:
        return {**say(x.reply or "Please enter one dish and a positive quantity, e.g. '2 burgers'."),
                "status": "INVALID_INPUT", "parsed_food_order": False}
    aliases = {"burgers": "burger", "burger": "burger", "pizzas": "pizza", "pizza": "pizza",
               "momo": "momos", "momos": "momos"}
    dish = aliases.get(x.dish_name.strip().lower(), x.dish_name.strip().lower())
    return {"dish_name": dish, "required_quantity": int(x.quantity), "available_quantity": "0",
            "status": "NEW", "parsed_food_order": True, "retry_order_requested": False,
            "partial_order_accepted": False}

def order_confirm(s: State) -> dict:
    available = MENU.get(s.get("dish_name", "").lower(), 0)
    requested = s.get("required_quantity", 0)
    status = "UNAVAILABLE" if available == 0 else ("AVAILABLE" if requested <= available else "PARTIAL")
    return {"available_quantity": str(available), "status": status}

def order_review(s: State) -> dict:
    remaining = s.get("order_retry_attempts", 0)
    if remaining <= 0:
        msg = user_facing("No order retries remain. Apologize and end the order without completing it.")
        print("\nAgent:", msg)
        return {**say(msg), "status": "REJECTED", "final_result": False, "retry_order_requested": False}
    status = s.get("status")
    if status == "INVALID_INPUT":
        prompt = f"Please enter one food item and a positive quantity, e.g. '2 burgers'. Attempts remaining: {remaining}."
    elif status == "PARTIAL":
        prompt = (f"Only {s['available_quantity']} {s['dish_name']}(s) are available; you requested "
                  f"{s['required_quantity']}. Reply 'accept partial' to order {s['available_quantity']}, "
                  f"or type a new order. Attempts remaining: {remaining}.")
    else:
        prompt = (f"Sorry, {s.get('dish_name', 'that dish')} is unavailable. Menu: burger, pizza, momos. "
                  f"Enter a new order with quantity. Attempts remaining: {remaining}.")
    print("\nAgent:", prompt)
    answer = input("You: ").strip()
    messages = [AIMessage(content=prompt), HumanMessage(content=answer)]
    if status == "PARTIAL" and answer.lower() in {"accept partial", "accept", "yes", "confirm", "go ahead", "ok", "okay"}:
        return {"messages": messages, "required_quantity": int(s["available_quantity"]), "status": "AVAILABLE",
                "partial_order_accepted": True, "retry_order_requested": False}
    return {"messages": messages, "order_retry_attempts": remaining - 1,
            "retry_order_requested": True, "partial_order_accepted": False, "status": "NEW"}

def cook(s: State) -> dict:
    if random.random() < COOK_SUCCESS:
        msg = user_facing(f"Cooking {s['required_quantity']} {s['dish_name']}(s) succeeded. Briefly tell the user the order is ready for serving.")
        print("\nAgent:", msg)
        return {**say(msg), "status": "READY"}
    remaining = max(0, s.get("cook_retry_attempts", 0) - 1)
    if remaining > 0:
        msg = user_facing(f"Cooking failed. {remaining} cook attempt remains. Tell the user the kitchen is retrying.")
        print("\nAgent:", msg)
        return {**say(msg), "status": "COOK_FAILED", "cook_retry_attempts": remaining}
    msg = user_facing("Cooking failed and no cook retries remain. Apologize and say the order cannot be completed.")
    print("\nAgent:", msg)
    return {**say(msg), "status": "COOK_FAILED", "cook_retry_attempts": 0, "final_result": False}

def serve(s: State) -> dict:
    if random.random() < SERVE_SUCCESS:
        msg = user_facing(f"The order of {s['required_quantity']} {s['dish_name']}(s) was served successfully. Tell the user their order is complete.")
        print("\nAgent:", msg)
        return {**say(msg), "status": "COMPLETE", "final_result": True}
    remaining = max(0, s.get("serve_retry_attempts", 0) - 1)
    if remaining > 0:
        msg = user_facing(f"Serving failed. {remaining} serve attempt remains. Briefly tell the user service is being retried.")
        print("\nAgent:", msg)
        return {**say(msg), "status": "SERVE_FAILED", "serve_retry_attempts": remaining}
    msg = user_facing("Serving failed and no serve retries remain. Apologize and say the order could not be completed.")
    print("\nAgent:", msg)
    return {**say(msg), "status": "SERVE_FAILED", "serve_retry_attempts": 0, "final_result": False}

def after_parse(s: State) -> Literal["confirm", "review", "end"]:
    if s.get("status") == "REJECTED": return "end"
    if s.get("status") == "INVALID_INPUT": return "review"
    return "confirm" if s.get("parsed_food_order") else "end"

def after_confirm(s: State) -> Literal["cook", "review"]:
    return "cook" if s.get("status") == "AVAILABLE" else "review"

def after_review(s: State) -> Literal["parse", "cook", "end"]:
    if s.get("status") == "AVAILABLE" and s.get("partial_order_accepted"): return "cook"
    if s.get("retry_order_requested"):
        # The newly entered order is the final allowed retry if the counter just reached 0.
        # If it is still unavailable/invalid, order_review will end the workflow.
        return "parse"
    return "end"

def after_cook(s: State) -> Literal["cook", "serve", "end"]:
    if s.get("status") == "READY": return "serve"
    if s.get("status") == "COOK_FAILED" and s.get("cook_retry_attempts", 0) > 0: return "cook"
    return "end"

def after_serve(s: State) -> Literal["cook", "end"]:
    if s.get("status") == "COMPLETE": return "end"
    if s.get("status") == "SERVE_FAILED" and s.get("serve_retry_attempts", 0) > 0 and s.get("cook_retry_attempts", 0) > 0:
        return "cook"
    return "end"

builder = StateGraph(State)
for name, fn in [("parse_order", parse_order), ("order_confirm", order_confirm),
                 ("order_review", order_review), ("cook", cook), ("serve", serve)]:
    builder.add_node(name, fn)
builder.add_edge(START, "parse_order")
builder.add_conditional_edges("parse_order", after_parse, {"confirm":"order_confirm", "review":"order_review", "end":END})
builder.add_conditional_edges("order_confirm", after_confirm, {"cook":"cook", "review":"order_review"})
builder.add_conditional_edges("order_review", after_review, {"parse":"parse_order", "cook":"cook", "end":END})
builder.add_conditional_edges("cook", after_cook, {"cook":"cook", "serve":"serve", "end":END})
builder.add_conditional_edges("serve", after_serve, {"cook":"cook", "end":END})
graph = builder.compile()

def main():
    print("=" * 54)
    print("RESTAURANT ORDERING AI AGENT")
    print("Menu stock:", MENU)
    print("Enter one dish and quantity, e.g. '2 burgers'.")
    print("=" * 54)
    first = input("\nYou: ").strip()
    initial: State = {
        "messages": [HumanMessage(content=first)],
        "dish_name": "", "required_quantity": 0, "available_quantity": "0",
        "status": "NEW", "order_retry_attempts": 3,
        "cook_retry_attempts": 2, "serve_retry_attempts": 2, "final_result": False,
        "retry_order_requested": False, "partial_order_accepted": False, "parsed_food_order": False,
    }
    result = graph.invoke(initial, config={"recursion_limit": 50})
    print("\n" + "=" * 54)
    print("Final status:", result.get("status", "UNKNOWN"))
    print("Order completed:", result.get("final_result", False))
    if result.get("dish_name"):
        print(f"Order: {result.get('required_quantity')} x {result.get('dish_name')}")
    print("=" * 54)

if __name__ == "__main__":
    main()
