import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import time
import re
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API NOT FOUND!!")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

#Tools
def get_weather(city):
    weather={
        "delhi":38,
        "mumbai":42,
        "banglore":26,
        "channai":50
    }
    return weather.get(city.lower(),"City not found!")

def calculator(expression):
    try:
        return eval(expression)
    except:
        return "calc error!"

tools={
    "get_weather":get_weather,
    "calculator":calculator
}

system_prompt="""
You are a weather assistant.
You have these tools:
get_weather(city)
calculator(expression)
Rules:
1.Decide what you need to next.
2.Call only one tool at a time.
3.After writing an ACTION,stop.
4.Never guess a tool result.
5.Wait for observation.
6.use this observation to decide your next step.
7.When the task is complete give the final answer.
FORMAT:
Thought:What you need to do?
Action:tool_name(arguement)
When finished:


"""
def run_agent(question):
    message_system={
        "role":"system",
        "content":system_prompt
    }
    message={
        "role":"user",
        "content":question
    }
    messages=[message_system,message]
    for step in range(6):
        print("\n-------------")
        print("STEP",step+1)
        print("---------------")
    
        response=client.chat.completions.create(model=model,messages=messages,temperature=0)
        answer=response.choices[0].message.content
        print(answer)

#Agent has finished
        if "Final Answer:" in answer:

            break
#find the action
        match=re.search(r'Action:\s*([a-zA-Z_]\w*)\((.*?)\)', answer)
        if match:
            tool_name=match.group(1) 
            tool_input=match.group(2)
            tool_input=tool_input.strip()
            tool_input=tool_input.strip('"').strip('"')
            print("Tool Name:", tool_name)
            print("Tool Input:", tool_input)
        #Run the tool 
            if tool_name in tools:
                   tool=tools[tool_name] 
                   observation=tool(tool_input)
            else: 
                   observation="tool not found"
                   print( "Observation:", observation )
 #add LLM response to memory
            messages.append({ "role":"assistant", "content":answer }) 
#Give tool result back to LLM 
            messages.append({ "role":"user", "content": "Observation: " + str(observation) })
            time.sleep(5)
        else:
            print("No Action Found.")
            break
    
prompt="""What is the temeperatue in Delhi and is it above 35? """
run_agent(prompt)