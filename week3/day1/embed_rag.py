import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("api not found")
client=Groq(api_key=my_api_key)
groqmodel="openai/gpt-oss-20b"

def cosine_similarity(a,b):
    return np.dot(a,b)/(
        np.linalg.norm(a) * np.linalg.norm(b)

    )
model=SentenceTransformer("all-MiniLM-L6-v2")


documents=[
    "Employees receive 24 days of paid leaves per year.",
    "Employee work from the offcie on Tuesday,Wednesday and Thrusday.",
    "Monday and Friday are optimal work-from-from days.",
    "Employees receive Rs. 3000 for gym reimbursement.",
    "Employees can claim Rs 2000 per month for home internet.",
    "Employee have a 90 day notice period."
]
documents_embedding=model.encode(documents)
def retrieve_info(q_embedding):
    scores=[]
    for i,document in enumerate(documents_embedding):
        score=cosine_similarity(q_embedding,document)
        scores.append((score,documents[i]))
    scores.sort(reverse=True)
    return scores[0]
def ask_llm(question,context):
    
    sys_prompt=f"""answer in one line only dont hallucinate.context:{context}"""
    system_msg={
        "role":"system",
        "content":sys_prompt
    }
    user_msg={
        "role":"user",
        "content":question
    }
    mesaages=[system_msg,user_msg]
    response=client.chat.completions.create(model=groqmodel,messages=mesaages)
    answer=response.choices[0].message.content
    return answer


query="How much vacation could i get?"

q_embedding=model.encode(query)
score,context=retrieve_info(q_embedding)
answer=ask_llm(query,context)
print(answer)