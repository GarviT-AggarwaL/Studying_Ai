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

from pydantic import BaseModel
class Ticket(BaseModel):
    name:str
    email:str
    issue:str
    address:str
    phone:str
schema=Ticket.model_json_schema()

response_format={
    "type":"json_object"
}

system_prompt=f"""
Extract the information from the customer ticket.

Return ONLY valid json.

Follow this schema exactly:
{schema}

"""
message_system={
    "role":"system",
    "content":system_prompt
}
text="Hello My name is Garvit . I have an phone which is not working at all. My address is delhi.My mails is abc@gmail.com.My contact no is 123456."

prompt=f"""
This is a customer ticket.Please extract the personal information from this.
{text}
"""
message={"role":role,
        "content":prompt}
messages=[message_system,message]
response=client.chat.completions.create(model=model,messages=messages,response_format=response_format)
print(response)

print("********************")
answer=response.choices[0].message.content
print(answer)

#isko padhte kaise hai
import json
raw_json=answer
data_file=json.loads(raw_json)
ticket=Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.address)
print(ticket.phone)

