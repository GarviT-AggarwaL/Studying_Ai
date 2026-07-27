import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
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


def step1_res_extract(RESUME):
    #extract skills from resume
    system_prompt="""
    You are a professional HR assistant.EXtract the skills from the candidate resume provided.
    Only return the skills no other information. Do not invent skills any info yourself.

    """
    user_prompt=f"""
    Extract the skills from resume
    {RESUME}

    """
    return ask_llm(system_prompt,user_prompt)



def step2_jd_extract():
    #extract skills from resume
    system_prompt="""
    You are a professional HR assistant.EXtract the skills from the job description provided.
    Only return the skills no other information. Do not invent skills any info yourself.

    """
    user_prompt=f"""
    Extract the skills from jd
    {JD}

    """
    return ask_llm(system_prompt,user_prompt)

def step3_match(candidate,jd):
    system_prompt="""
    You are professional HR assistant, compare the skill of candidate resume and jd and give a final score between 1 to 100 also predict a short verdict whether candidate is good fit or not for the role.


    """
    user_prompt=f"""
    comapre and match the skills
    JD:
    {jd}
    Candidate:
    {candidate}
    """
    return ask_llm(system_prompt,user_prompt)


candidate=step1_res_extract(RESUME)
sleep(2)
jd=step2_jd_extract()
sleep(2)
score=step3_match(candidate,jd)
sleep(2)
print(score)