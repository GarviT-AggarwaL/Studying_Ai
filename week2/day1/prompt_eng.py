import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("api error")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"


def llm_ans(prompt):
    message={
        "role":"user",
        "content":prompt
    }
    messages=[message]
    response=client.chat.completions.create(model=model,messages=messages)
    ans=response.choices[0].message.content
    return ans
bad_prompt="""
#ROLE:
You are a support assistant at a mobile/laptop company.
#Task
You have to classify the issue in a category.
#Constraint
You have to classify the issue in one of the three categories namely billing,technical,return.
#Output_Format
Your answer should be in one word only. The one word should be one of the categories given in constarints.
#Example
For instance if a user complain says he wants a refund then the category is Return.
#FallBack
If the issue is unrealted to any of the categories mentioned in constarints, then the answer should be OTHER.
This is a user complaint.
My Phone is not working.

"""
print(llm_ans(bad_prompt))