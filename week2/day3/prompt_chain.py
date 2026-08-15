import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import time
load_dotenv()
from time import sleep
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("api error")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"



JD="""
We are hiring a backend python developer.

Requirements:
- Strong Python
- FastApi or Django
- Postgresql
- Docker
- AWS
- Best APis
- 2+ years of experience
"""
RESUME="""
Name: Rahul Sharma
Experience:
3 years as a software engineer.
Skills:
Python,Fastapi,mysql,docker,rest apis,git
projects:
Build a food delivery backend using fastapi and mysql.
"""
def ask_llm(system_prompt,user_prompt):
    sys_msg={
        "role":"system",
        "content":system_prompt
    }
    user_msg={
        "role":"user",
        "content":user_prompt
    }
    messages=[sys_msg,user_msg]
    response=client.chat.completions.create(model=model,messages=messages)
    answer=response.choices[0].message.content
    return answer
def step1_res_extract():
    #extract skilld from resume
    system_prompt="""
    You are a professional HR assistant. Extract the skills from candidate resume provided.Only return the skills no other information.
    Do not invent any skills information on your own.
    """
    user_prompt=f"""
    Extract The skills from resume.{RESUME}
    """
    return ask_llm(system_prompt,user_prompt)
def step2_jd_extract():
    #extract skilld from jd
    system_prompt="""
    You are a professional HR assistant. Extract the skills from Job description provided.Only return the skills no other information.
    Do not invent any skills information on your own.
    """
    user_prompt=f"""
    Extract The skills from Job description.{JD}
    """
    return ask_llm(system_prompt,user_prompt)

def step3_match(candidate,jd):
    #extract skilld from resume
    system_prompt="""
    You are a professional HR assistant.Compare the skills of candidate and skills required in Jd and provide a final score between 1 to 100 and provide a final verdict whether the candidate is fit for the job role or not.
    """
    user_prompt=f"""
    Compare and match the skills.
    JD:{jd}
    Candidate:{candidate}
    """
    return ask_llm(system_prompt,user_prompt)
candidate=step1_res_extract()
print(candidate)

time.sleep(5)
jd=step2_jd_extract()
print(jd)
time.sleep(5)
score=step3_match(candidate,jd)
print(score)
time.sleep(5)
