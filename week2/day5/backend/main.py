from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from pypdf import PdfReader
from dotenv import load_dotenv
from groq import Groq

from pydantic import BaseModel, Field

import os
import json


# --------------------------------
# ENVIRONMENT
# --------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found")


client = Groq(api_key=api_key)

model = "llama-3.3-70b-versatile"


# --------------------------------
# FASTAPI
# --------------------------------

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# DATA MODELS
# --------------------------------

class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    github: str | None = None
    demo: str | None = None


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = Field(default_factory=list)

    experience: list[Experience] = Field(
        default_factory=list
    )

    education: list[str] = Field(
        default_factory=list
    )

    projects: list[Project] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )


resume_schema = Resume.model_json_schema()


class ChatRequest(BaseModel):
    question: str


# --------------------------------
# READ PDF
# --------------------------------

def read_pdf(file_path: Path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# --------------------------------
# PARSE RESUME
# --------------------------------

def parse_resume(resume_text: str):

    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning.

Return ONLY valid JSON matching this schema:

{resume_schema}

Rules:

1. Never invent information.
2. If information is unavailable, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experience.
5. Extract skills from the entire resume.
6. For projects extract:
   - name
   - description
   - technologies
   - GitHub URL if explicitly present
   - demo URL if explicitly present
7. Never guess GitHub or demo URLs.
"""

    response = client.chat.completions.create(
        model=model,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Parse this resume:\n\n{resume_text}"
            }
        ],

        response_format={
            "type": "json_object"
        },

        temperature=0
    )

    raw_output = response.choices[0].message.content

    data = json.loads(raw_output)

    return Resume(**data)


# --------------------------------
# AI CHAT
# --------------------------------

def ask_candidate(
    question: str,
    resume: Resume
):

    system_prompt = f"""
You are Garvit Aggarwal's AI portfolio assistant.

You are answering questions about Garvit.

Here is the verified information from his resume:

{resume.model_dump_json(indent=2)}

Rules:

1. Answer ONLY using the information provided above.
2. Never invent information.
3. Never claim Garvit has experience that is not listed.
4. If the information is unavailable, say:
   "I don't have enough information to answer that."
5. Be professional and concise.
6. Answer as if you are representing Garvit to a recruiter.
7. When discussing projects, mention relevant technologies when available.
"""

    response = client.chat.completions.create(

        model=model,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content


# --------------------------------
# HOME
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "Garvit AI Portfolio API is running!"
    }


# --------------------------------
# PROFILE
# --------------------------------

@app.get("/profile")
def profile():

    resume_text = read_pdf(
        Path("Gravity_resume.pdf")
    )

    resume = parse_resume(resume_text)

    return resume.model_dump()


# --------------------------------
# CHAT
# --------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    resume_text = read_pdf(
        Path("Gravity_resume.pdf")
    )

    resume = parse_resume(resume_text)

    answer = ask_candidate(
        request.question,
        resume
    )

    return {
        "answer": answer
    }