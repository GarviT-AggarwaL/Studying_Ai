import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API KEY ERROR!!!")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
prompt="Tell me details about Indian Cricket Team"
role="user"
message={
    "role":role,
    "content":prompt
}
messages=[message]
response=client.chat.completions.create(model=model,messages=messages)
print(response)
print("***************************")
answer=response.choices[0].message.content
print(answer)