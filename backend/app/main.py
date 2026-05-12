from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from groq import Groq
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch
import os
import PyPDF2
import io
import json
import tempfile
import rezorpay

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://astounding-cajeta-fefd31.netlify.app", "https://resume-score.netlify.app"],
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
                "content": f"""Analyze this resume and respond in JSON only, nothing else:

Resume:
{resume_text}

Respond in this exact JSON format:
{{
    "ats_score": <number between 0-100>,
    "strengths": [<3 strong points>],
    "improvements": [<3 improvement suggestions>],
    "missing_keywords": [<important missing keywords>]
}}"""
            }
        ]
    )

    clean = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    result = json.loads(clean)
    return result


@app.post("/generate-report")
async def generate_report(file: UploadFile = File(...)):
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
                "content": f"""Analyze this resume and respond in JSON only, nothing else:

Resume:
{resume_text}

Respond in this exact JSON format:
{{
    "ats_score": <number between 0-100>,
    "strengths": [<3 strong points>],
    "improvements": [<3 improvement suggestions>],
    "missing_keywords": [<important missing keywords>]
}}"""
            }
        ]
    )

    clean = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    result = json.loads(clean)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("title", fontSize=24, fontName="Helvetica-Bold",
                                  textColor=colors.HexColor("#4f46e5"), spaceAfter=4)
    sub_style = ParagraphStyle("sub", fontSize=11, fontName="Helvetica",
                                textColor=colors.HexColor("#6b7280"), spaceAfter=20)
    heading_style = ParagraphStyle("heading", fontSize=14, fontName="Helvetica-Bold",
                                    textColor=colors.HexColor("#1e1b4b"), spaceAfter=8, spaceBefore=16)
    body_style = ParagraphStyle("body", fontSize=11, fontName="Helvetica",
                                 textColor=colors.HexColor("#374151"), spaceAfter=6, leading=16)

    story.append(Paragraph("AI Resume Scorer", title_style))
    story.append(Paragraph("Your personalized ATS analysis report", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 16))

    score = result["ats_score"]
    if score >= 80:
        score_color = "#22c55e"
    elif score >= 60:
        score_color = "#f59e0b"
    else:
        score_color = "#ef4444"

    story.append(Paragraph("ATS Score", heading_style))
    story.append(Paragraph(f'<font color="{score_color}" size="28"><b>{score}/100</b></font>', styles["Normal"]))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))

    story.append(Paragraph("Strengths", heading_style))
    for s in result["strengths"]:
        story.append(Paragraph(f"✓  {s}", body_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    story.append(Paragraph("Areas for Improvement", heading_style))
    for imp in result["improvements"]:
        story.append(Paragraph(f"→  {imp}", body_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    story.append(Paragraph("Missing Keywords", heading_style))
    keywords = "  |  ".join(result["missing_keywords"])
    story.append(Paragraph(keywords, body_style))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Generated by AI Resume Scorer • resume-score.netlify.app",
                            ParagraphStyle("footer", fontSize=9, textColor=colors.HexColor("#9ca3af"))))

    doc.build(story)

    return FileResponse(tmp.name, media_type="application/pdf",
                        filename="resume_report.pdf")


@app.post("/generate-resumes")
async def generate_resumes(file: UploadFile = File(...)):
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
                "content": f"""You are an expert resume writer. Based on this resume, create 3 different ATS-optimized versions.

Resume:
{resume_text}

Respond in this exact JSON format only, nothing else:
{{
    "resumes": [
        {{
            "title": "Software Engineer Focus",
            "content": "<full resume text here, properly formatted>"
        }},
        {{
            "title": "Full Stack Developer Focus",
            "content": "<full resume text here, properly formatted>"
        }},
        {{
            "title": "Backend Developer Focus",
            "content": "<full resume text here, properly formatted>"
        }}
    ]
}}"""
            }
        ]
    )

    clean = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    result = json.loads(clean, strict=False)
    return result

    @app.post("/create-order")
async def create_order():
    rz_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))
    order = rz_client.order.create({
        "amount": 14900,
        "currency": "INR",
        "payment_capture": 1
    })
    return {"order_id": order["id"], "amount": order["amount"], "currency": order["currency"]}


@app.post("/verify-payment")
async def verify_payment(data: dict):
    rz_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))
    try:
        rz_client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })
        return {"success": True}
    except:
        return {"success": False}