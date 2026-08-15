import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API ERROR")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
prompt="Explain me about system role and temperatur in simple words."
message_system={
    "role":"system",
    "content":"You are Chief Ai Engineer in a MNC."

}
message={
    "role":"user",
    "content":prompt
}
messages=[message_system,message]
response=client.chat.completions.create(model=model,messages=messages,temperature=0)
print(response)
print("*********")
answer=response.choices[0].message.content
print(answer)