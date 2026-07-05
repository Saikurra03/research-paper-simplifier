"""
AI Resume Analyzer
==================
Analyzes resumes and generates structured feedback and improvement suggestions
using the Cohere API.

Version: 1.0.0
"""

import os
import json
import requests
import threading
import webbrowser
import fitz
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import Optional, Dict, Any, Tuple

load_dotenv()


COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("Set the COHERE_API_KEY environment variable")

COHERE_URL = "https://api.cohere.com/v2/chat"

VALID_EXPERIENCE_LEVELS = ["fresher", "mid_level", "experienced"]

LEVEL_DISPLAY_NAMES = {
    "fresher": "Fresher / Student",
    "mid_level": "Mid-Level (2-5 years)",
    "experienced": "Senior (5+ years)"
}


def validate_request_data(data: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    if not data:
        return False, "No data provided in request"

    resume_text = data.get("resume")
    if not resume_text or not resume_text.strip():
        return False, "Resume content is required"

    if len(resume_text.strip()) < 30:
        return False, "Resume content is too short. Please provide a complete resume."

    return True, None


def call_cohere(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": "command-a-03-2025",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    response = requests.post(COHERE_URL, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        error_detail = response.text[:500]
        raise Exception(f"Cohere API error ({response.status_code}): {error_detail}")

    result = response.json()

    if "message" not in result or "content" not in result["message"]:
        raise Exception("No response from AI model")

    return result["message"]["content"][0]["text"]


def resume_prompt(resume_text: str, job_role: str, experience_level: str) -> str:
    level_display = LEVEL_DISPLAY_NAMES.get(experience_level, "Fresher / Student")

    return f"""
You are an experienced HR professional and career coach who analyzes resumes and gives detailed, actionable feedback. Your goal is to help the candidate improve their resume and land their target job.

CRITICAL INSTRUCTIONS:
1. Be honest about weaknesses - don't sugarcoat
2. Give specific, actionable improvements (not generic advice)
3. Score each section fairly
4. Compare against what top candidates in this role typically have
5. Format output in clean Markdown with ## headings

RESUME TO ANALYZE:
{resume_text}

TARGET JOB ROLE: {job_role if job_role else "General / Not specified"}
EXPERIENCE LEVEL: {level_display}

GENERATE ALL 15 SECTIONS:

## 1. Overall Score
Give a score out of 100 with a brief justification.

## 2. Quick Summary
2-3 sentences about what this resume does well and what needs work.

## 3. Contact Information
Check if contact details are complete (name, email, phone, LinkedIn, location). What's missing?

## 4. Professional Summary / Objective
Is there a strong opening summary? Rate it and suggest improvements.

## 5. Skills Assessment
List the key skills found. Rate how well they match the target role. What's missing?

## 6. Work Experience Analysis
Evaluate the work experience section. Are achievements quantified? Is it results-focused?

## 7. Education
Review the education section. Any improvements needed?

## 8. Projects / Portfolio
Are projects relevant and well-described? Suggestions for improvement.

## 9. Formatting & Design
Is the resume well-structured? Check consistency, spacing, fonts, length.

## 10. ATS Compatibility
Will this resume pass Applicant Tracking Systems? Check for keywords, formatting issues.

## 11. Keywords Found
List important keywords found in the resume.

## 12. Missing Keywords
What important keywords for this role are missing?

## 13. Top 5 Improvements
List the 5 most important changes to make, ranked by impact.

## 14. Red Flags
Any issues that might turn off recruiters (typos, gaps, irrelevant info, etc.)

## 15. Improved Version
Rewrite the professional summary and one work experience bullet point in a stronger way.
"""


app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


@app.route('/')
def serve_index() -> str:
    return send_from_directory('.', 'index.html')


@app.route("/api/analyze", methods=["POST"])
def analyze_resume() -> Tuple[Dict[str, Any], int]:
    try:
        data = request.json

        is_valid, error_message = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        resume_text = data.get("resume").strip()
        job_role = data.get("role", "")
        experience_level = data.get("level", "fresher")

        result = call_cohere(
            resume_prompt(resume_text, job_role, experience_level)
        )

        return jsonify({
            "result": result,
            "level": LEVEL_DISPLAY_NAMES.get(experience_level, "Fresher / Student")
        }), 200

    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500


@app.route("/api/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        page_count = len(doc)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"

        doc.close()

        if len(text.strip()) < 30:
            return jsonify({"error": "Could not extract enough text from PDF."}), 400

        return jsonify({"text": text, "pages": page_count}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    URL = f"http://127.0.0.1:{PORT}"
    print(f"\n  Open this in your browser: {URL}\n")
    threading.Timer(1.0, lambda: webbrowser.open(URL)).start()
    app.run(host="127.0.0.1", port=PORT, debug=True)
