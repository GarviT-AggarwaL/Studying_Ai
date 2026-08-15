import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API NOT FOUND!!")
client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"
prompt1="Explain me about tokens in one line."
prompt2="Explain me Entrepreneurship in one paragraph."
prompt3="Tell the MBA types and fields in MBA"
prompts=[prompt1,prompt2,prompt3]
for prompt in prompts:
    message={
       "role":role,
       "content":prompt
    }
    messages=[message]
    response=client.chat.completions.create(model=model,messages=messages,max_tokens=500)
    usage=response.usage
    print(f"prompt : {prompt} --> Your Tokens : {usage.prompt_tokens} Completions Tokens : {usage.completion_tokens} Total Tokens : {usage.total_tokens} Finish Reason : {response.choices[0].finish_reason}")

    #answer=response.choices[0].message.content
    #print(answer)