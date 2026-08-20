import os
from dotenv import load_dotenv
from groq import Groq
from pathlib import Path
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("api key not found")
client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"
#step1 to create a knowledge base
knowledge_base={
    "age":"Garvit's Age is 22 years.",
    "net_worth":"Garvit's net worth is 2000."
}
def retrieve_info(question):
    question=question.lower()
    if "age" in question:
        return knowledge_base["age"]
    elif "net_worth" in question:
        return knowledge_base["net_worth"]
    else:
        return None
def ask_llm(question):
    context=retrieve_info(question)
    sys_prompt=f"""Answer in one line only.Answer show be according to context only.Context : {context}.Dont hallucinate"""
    sys_msg={
        "role":"system",
        "content":sys_prompt
    }
    user_msg={
        "role":"user",
        "content":question
    }
    messages=[sys_msg,user_msg]
    response=client.chat.completions.create(model=model,messages=messages)
    answer=response.choices[0].message.content
    print(answer)
question="What is net_worth of garvit ?"
ask_llm(question)