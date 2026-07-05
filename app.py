"""
AI Research Paper Simplifier
============================
Analyzes research papers and generates structured educational content
using the Cohere API.

Architecture:
    - Flask backend serving REST API
    - Cohere API for AI inference
    - Static HTML/CSS/JS frontend (SPA)

Version: 4.0.0
"""

import os
import io
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


# =============================================================================
# Configuration
# =============================================================================

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("Set the COHERE_API_KEY environment variable")

COHERE_URL = "https://api.cohere.com/v2/chat"

VALID_EXPLANATION_LEVELS = ["school_student", "college_student", "researcher"]

LEVEL_DISPLAY_NAMES = {
    "school_student": "School Student",
    "college_student": "College Student",
    "researcher": "Researcher"
}

LEVEL_DESCRIPTIONS = {
    "school_student": "a school student (age 14-18) with basic science knowledge",
    "college_student": "a college undergraduate student with foundational knowledge in the field",
    "researcher": "a fellow researcher with advanced domain expertise"
}


# =============================================================================
# Helper Functions
# =============================================================================

def validate_explanation_level(level: str) -> bool:
    return level in VALID_EXPLANATION_LEVELS


def validate_request_data(data: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    if not data:
        return False, "No data provided in request"

    paper_text = data.get("paper")

    if not paper_text or not paper_text.strip():
        return False, "Research paper content is required"

    if len(paper_text.strip()) < 50:
        return False, "Paper content is too short. Please provide a complete research paper."

    explanation_level = data.get("level", "college_student")

    if not validate_explanation_level(explanation_level):
        valid_levels = ", ".join(VALID_EXPLANATION_LEVELS)
        return False, f"Invalid explanation level. Must be one of: {valid_levels}"

    return True, None


def call_cohere(prompt: str) -> str:
    """Call Cohere Chat API with the given prompt."""
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": "command-a-03-2025",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
    }

    response = requests.post(
        COHERE_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        error_detail = response.text[:500]
        raise Exception(f"Cohere API error ({response.status_code}): {error_detail}")

    result = response.json()

    if "message" not in result or "content" not in result["message"]:
        raise Exception("No response from AI model")

    return result["message"]["content"][0]["text"]


# =============================================================================
# Prompt Engineering
# =============================================================================

def research_paper_prompt(paper_text: str, explanation_level: str) -> str:
    target_audience = LEVEL_DESCRIPTIONS.get(
        explanation_level,
        LEVEL_DESCRIPTIONS["college_student"]
    )
    level_display = LEVEL_DISPLAY_NAMES.get(
        explanation_level,
        "College Student"
    )

    return f"""
You are an experienced university professor and research mentor who explains complex research papers in simple, structured, and educational language. Your goal is to make research accessible to {target_audience}.

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE STRICTLY:

1. AVOID HALLUCINATIONS: Use ONLY information available in the provided paper
2. BE HONEST: If information is missing or unclear, explicitly state "Not mentioned in the paper"
3. FORMAT: Produce well-formatted Markdown output with clear headings (##) and bullet points
4. TONE: Keep explanations educational, accurate, and engaging
5. NO INVENTION: Do NOT invent data, statistics, conclusions, or methodologies not present in the paper
6. COMPLETENESS: Address ALL 25 sections listed below
7. CONCISENESS: Be thorough but avoid unnecessary verbosity

RESEARCH PAPER TO ANALYZE:
{paper_text}

TARGET EXPLANATION LEVEL: {level_display}

REQUIRED OUTPUT - GENERATE ALL 25 SECTIONS:

## 1. Paper Title
Extract the exact title from the paper.

## 2. Research Domain
Identify the primary research domain (e.g., Computer Science, Biology, Physics, Medicine, etc.) and sub-domain if applicable.

## 3. Executive Summary
Provide a concise 3-5 sentence summary capturing the essence of the paper.

## 4. Explain Like I'm 10 Years Old
Explain the core idea of this paper in extremely simple language that a 10-year-old could understand. Use analogies and simple words. Avoid ANY technical jargon.

## 5. Undergraduate-Level Explanation
Explain the paper's content at a level appropriate for college undergraduates. Include relevant background context and moderate technical details.

## 6. Researcher-Level Explanation
Provide a technical, in-depth explanation suitable for fellow researchers. Include methodology details, theoretical foundations, and technical nuances.

## 7. Problem Statement
What specific problem does this paper address? State it clearly and concisely in 2-3 sentences.

## 8. Why This Research Was Needed
Explain the motivation behind this research. Why was this problem worth solving? What gap does it fill?

## 9. Existing Challenges
What were the limitations or challenges in previous approaches or the current state of the field before this research?

## 10. Proposed Solution
Describe the solution proposed by the authors in clear, structured terms. What is the core innovation?

## 11. Methodology (Step-by-Step)
Break down the methodology into clear, numbered steps.

## 12. Workflow / Architecture
If applicable, describe the system workflow, architecture, or process flow.

## 13. Key Contributions
List the main contributions of this paper as bullet points.

## 14. Advantages
What are the advantages of the proposed approach over existing methods?

## 15. Limitations
What are the acknowledged limitations of this research?

## 16. Future Scope
What future work do the authors suggest or what directions emerge from this research?

## 17. Important Keywords
List 10-15 important keywords from this paper, comma-separated.

## 18. Technical Terms with Simple Explanations
Identify 8-12 technical terms used in the paper and provide simple explanations.

## 19. Real-World Applications
Where could this research be applied in the real world? List 4-6 specific use cases.

## 20. Key Takeaways
Provide 5-7 key takeaways from this paper in bullet point format.

## 21. Flashcards
Create 8-10 flashcards for studying this paper (Q&A format).

## 22. Multiple Choice Questions (MCQs)
Create 5 MCQs to test understanding with answers.

## 23. Viva Questions
Provide 8-10 viva questions that a student might be asked when presenting this paper.

## 24. Technical Interview Questions
Create 5-7 technical interview questions related to this paper's domain and methodology.

## 25. Suggested Future Research Ideas
Propose 3-5 original future research ideas that build upon this paper's work.

IMPORTANT REMINDER:
- Prioritize ACCURACY over COMPLETENESS
- If any section cannot be adequately filled from the paper content, explicitly state: "Information not available in the provided paper"
- Do NOT guess or infer beyond what is stated in the paper
"""


# =============================================================================
# Flask Application
# =============================================================================

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


@app.route('/')
def serve_index() -> str:
    return send_from_directory('.', 'index.html')


@app.route("/api/analyze", methods=["POST"])
def analyze_research_paper() -> Tuple[Dict[str, Any], int]:
    try:
        data = request.json

        is_valid, error_message = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        paper_text = data.get("paper").strip()
        explanation_level = data.get("level", "college_student")

        result = call_cohere(
            research_paper_prompt(paper_text, explanation_level)
        )

        return jsonify({
            "result": result,
            "level": LEVEL_DISPLAY_NAMES.get(explanation_level, "College Student")
        }), 200

    except Exception as e:
        print(f"Error analyzing research paper: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500


@app.route("/api/upload", methods=["POST"])
def upload_pdf():
    """Extract text from an uploaded PDF file."""
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

        if len(text.strip()) < 50:
            return jsonify({"error": "Could not extract enough text from PDF. The file may be image-based."}), 400

        return jsonify({"text": text, "pages": page_count}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500


@app.route("/api/models", methods=["GET"])
def list_models():
    models = [
        {"id": "command-a-03-2025", "name": "Command A (Latest)", "provider": "Cohere"},
        {"id": "command-r-plus-08-2024", "name": "Command R+", "provider": "Cohere"},
        {"id": "command-r", "name": "Command R", "provider": "Cohere"},
    ]
    return jsonify({"models": models, "default": "command-a-03-2025"})


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    URL = f"http://127.0.0.1:{PORT}"
    print(f"\n  Open this in your browser: {URL}\n")
    threading.Timer(1.0, lambda: webbrowser.open(URL)).start()
    app.run(host="127.0.0.1", port=PORT, debug=True)
