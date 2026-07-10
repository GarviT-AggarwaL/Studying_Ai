
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
role="user"
prompt="suggest a name for my grocery dryfruits company"
#System
message_system={
    "role":"system",
    "content":"you are a brand manager and suggest name for my company"
}
#message mein role and content
message={"role":role,
        "content":prompt}
messages=[message_system,message]
# Temperature by default is 0 meaning safe
response=client.chat.completions.create(model=model,messages=messages,temperature=2)
print(response)

print("********************")
answer=response.choices[0].message.content
print(answer)