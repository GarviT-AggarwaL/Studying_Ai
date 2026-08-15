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
from pydantic import BaseModel
class Ticket(BaseModel):
    Company_name:str
    Car_driven:int
    Address:str
    Condition:str
schema=Ticket.model_json_schema()  
response_format={
    "type":"json_object",
}

system_prompt=f"""
Extract the information from the ticket strictly based on the schema and give me json output.{schema}
"""
message_system={
    "role":"system",
    "content":system_prompt
}


text="Hello I want to sell my car.My address is Delhi.The company is NISSAN and year of purchase is 2011 and its variant is petrol.Engine is of 1500cc power.Car is extremely in best condition and only 75000 km driven.All functions of car are properly working."
prompt=f"""
This is Basically a customer ticket and extract the main information from this{text}
"""
message={
    "role":"user",
    "content":prompt
}
messages=[message_system,message]
response=client.chat.completions.create(model=model,messages=messages,response_format=response_format)
answer=response.choices[0].message.content
print(answer)

import json
raw_jsons=answer
data_file=json.loads(raw_jsons)
ticket=Ticket(**data_file)
print(ticket.Car_driven)
print(ticket.Address)
print(ticket.Company_name)
print(ticket.Condition)
