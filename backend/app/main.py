from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
import os
import PyPDF2
import io
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://astounding-cajeta-fefd31.netlify.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Resume Scorer API chal raha hai!"}

@app.post("/score-resume")
async def score_resume(file: UploadFile = File(...)):
    pdf_content = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))

    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""Yeh resume analyze karo aur sirf JSON format mein response do, kuch aur mat likho:

Resume:
{resume_text}

Yeh exact JSON format mein response do:
{{
    "ats_score": <0 se 100 ke beech number>,
    "strengths": [<3 strong points>],
    "improvements": [<3 improvement suggestions>],
    "missing_keywords": [<important keywords jo resume mein nahi hain>]
}}"""
            }
        ]
    )

    clean = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    result = json.loads(clean)
    return result