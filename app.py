"""
AI Research Paper Simplifier
============================
Refactored from Resume Analyzer

This application analyzes research papers and generates structured educational content
using the Google Gemini API. Designed to help students and researchers understand
complex papers at their preferred comprehension level.

Architecture:
    - Flask backend serving REST API
    - Google Gemini 2.5 Flash for AI analysis
    - Static HTML/CSS/JS frontend

Author: Refactored by Senior Python Engineer
Version: 2.0.0
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import threading
import webbrowser
from typing import Optional, Dict, Any, Tuple


# =============================================================================
# Configuration
# =============================================================================

# Configure Gemini API
# IMPORTANT: Replace with your actual API key
genai.configure(api_key="YOUR_API_KEY_HERE")

# Initialize Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# Valid explanation levels
VALID_EXPLANATION_LEVELS = ["school_student", "college_student", "researcher"]

# User-friendly display names for explanation levels
LEVEL_DISPLAY_NAMES = {
    "school_student": "School Student",
    "college_student": "College Student",
    "researcher": "Researcher"
}

# Level descriptions for prompt context
LEVEL_DESCRIPTIONS = {
    "school_student": "a school student (age 14-18) with basic science knowledge",
    "college_student": "a college undergraduate student with foundational knowledge in the field",
    "researcher": "a fellow researcher with advanced domain expertise"
}


# =============================================================================
# Helper Functions
# =============================================================================

def validate_explanation_level(level: str) -> bool:
    """
    Validate if the provided explanation level is supported.
    
    Args:
        level: The explanation level string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return level in VALID_EXPLANATION_LEVELS


def validate_request_data(data: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Validate the incoming request data for the analyze endpoint.
    
    Performs validation checks on:
    - Presence of request data
    - Paper content existence and minimum length
    - Explanation level validity
    
    Args:
        data: Dictionary containing request payload
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
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


# =============================================================================
# Prompt Engineering
# =============================================================================

def research_paper_prompt(paper_text: str, explanation_level: str) -> str:
    """
    Generate a structured prompt for analyzing research papers.
    
    The prompt instructs Gemini to behave as an experienced university professor
    and research mentor who explains complex research papers in simple,
    structured, and educational language.
    
    The prompt is designed to:
    - Prevent hallucinations by explicitly restricting to paper content
    - Generate all 25 required sections
    - Adapt explanations based on target audience level
    - Produce clean, well-formatted Markdown output
    
    Args:
        paper_text: The full text of the research paper
        explanation_level: Target audience level 
                          (school_student, college_student, researcher)
        
    Returns:
        str: Formatted prompt for Gemini API
    """
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

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE STRICTLY:
═══════════════════════════════════════════════════════════════════════════════

1. AVOID HALLUCINATIONS: Use ONLY information available in the provided paper
2. BE HONEST: If information is missing or unclear, explicitly state "Not mentioned in the paper"
3. FORMAT: Produce well-formatted Markdown output with clear headings (##) and bullet points
4. TONE: Keep explanations educational, accurate, and engaging
5. NO INVENTION: Do NOT invent data, statistics, conclusions, or methodologies not present in the paper
6. COMPLETENESS: Address ALL 25 sections listed below
7. CONCISENESS: Be thorough but avoid unnecessary verbosity

═══════════════════════════════════════════════════════════════════════════════
RESEARCH PAPER TO ANALYZE:
═══════════════════════════════════════════════════════════════════════════════

{paper_text}

═══════════════════════════════════════════════════════════════════════════════
TARGET EXPLANATION LEVEL: {level_display}
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
REQUIRED OUTPUT - GENERATE ALL 25 SECTIONS:
═══════════════════════════════════════════════════════════════════════════════

## 1. 📄 Paper Title
Extract the exact title from the paper.

## 2. 🔬 Research Domain
Identify the primary research domain (e.g., Computer Science, Biology, Physics, Medicine, etc.) and sub-domain if applicable.

## 3. 📋 Executive Summary
Provide a concise 3-5 sentence summary capturing the essence of the paper.

## 4. 🧒 Explain Like I'm 10 Years Old
Explain the core idea of this paper in extremely simple language that a 10-year-old could understand. Use analogies and simple words. Avoid ANY technical jargon.

## 5. 🎓 Undergraduate-Level Explanation
Explain the paper's content at a level appropriate for college undergraduates. Include relevant background context and moderate technical details.

## 6. 👨‍🔬 Researcher-Level Explanation
Provide a technical, in-depth explanation suitable for fellow researchers. Include methodology details, theoretical foundations, and technical nuances.

## 7. ❓ Problem Statement
What specific problem does this paper address? State it clearly and concisely in 2-3 sentences.

## 8. 💡 Why This Research Was Needed
Explain the motivation behind this research. Why was this problem worth solving? What gap does it fill?

## 9. 🚧 Existing Challenges
What were the limitations or challenges in previous approaches or the current state of the field before this research?

## 10. ✅ Proposed Solution
Describe the solution proposed by the authors in clear, structured terms. What is the core innovation?

## 11. 📊 Methodology (Step-by-Step)
Break down the methodology into clear, numbered steps:
1. Step one
2. Step two
...and so on

## 12. 🏗️ Workflow / Architecture
If applicable, describe the system workflow, architecture, or process flow. Use text-based representation if diagrams are mentioned.

## 13. 🏆 Key Contributions
List the main contributions of this paper as bullet points:
- Contribution 1
- Contribution 2
...

## 14. ➕ Advantages
What are the advantages of the proposed approach over existing methods? List as bullet points.

## 15. ➖ Limitations
What are the acknowledged limitations of this research? Be honest about what the paper itself admits.

## 16. 🔮 Future Scope
What future work do the authors suggest or what directions emerge from this research?

## 17. 🏷️ Important Keywords
List 10-15 important keywords from this paper, comma-separated.

## 18. 📖 Technical Terms with Simple Explanations
Identify 8-12 technical terms used in the paper and provide simple explanations:
- **Term 1**: Simple explanation
- **Term 2**: Simple explanation
...

## 19. 🌍 Real-World Applications
Where could this research be applied in the real world? List 4-6 specific use cases with brief descriptions.

## 20. 📌 Key Takeaways
Provide 5-7 key takeaways from this paper in bullet point format.

## 21. 🃏 Flashcards
Create 8-10 flashcards for studying this paper:
**Q:** [Question]
**A:** [Answer]

---

## 22. 📝 Multiple Choice Questions (MCQs)
Create 5 MCQs to test understanding:
**Q1:** [Question]
a) [Option]
b) [Option]
c) [Option]
d) [Option]
**Answer:** [Correct option letter with brief explanation]

---

## 23. 🎤 Viva Questions
Provide 8-10 viva questions that a student might be asked when presenting this paper:
**Q:** [Question]
**Expected Answer:** [Brief answer]

---

## 24. 💼 Technical Interview Questions
Create 5-7 technical interview questions related to this paper's domain and methodology:
**Q:** [Question]
**Detailed Answer:** [Comprehensive answer]

---

## 25. 🚀 Suggested Future Research Ideas
Propose 3-5 original future research ideas that build upon this paper's work:
1. **Idea Title**: Brief description
2. **Idea Title**: Brief description
...

═══════════════════════════════════════════════════════════════════════════════
IMPORTANT REMINDER:
═══════════════════════════════════════════════════════════════════════════════
- Prioritize ACCURACY over COMPLETENESS
- If any section cannot be adequately filled from the paper content, explicitly state: "Information not available in the provided paper"
- Do NOT guess or infer beyond what is stated in the paper
- Use emojis in section headers as shown above for visual organization
"""


# =============================================================================
# Flask Application
# =============================================================================

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend communication


@app.route('/')
def serve_index() -> str:
    """
    Serve the main index.html file.
    
    This endpoint serves the single-page application frontend.
    All other routing is handled client-side.
    
    Returns:
        str: HTML content of the main page
    """
    return send_from_directory('.', 'index.html')


@app.route("/analyze", methods=["POST"])
def analyze_research_paper() -> Tuple[Dict[str, Any], int]:
    """
    Analyze a research paper and generate structured educational content.
    
    This is the primary API endpoint. It accepts research paper text and
    an explanation level, then uses Gemini AI to generate comprehensive
    analysis across 25 different sections.
    
    Expected JSON Payload:
        {
            "paper": "Full text of the research paper...",
            "level": "school_student" | "college_student" | "researcher"
        }
    
    Returns:
        Tuple[Dict, int]: JSON response with analysis results or error message
        Success: {"result": "...", "level": "..."} with status 200
        Error: {"error": "..."} with status 400 or 500
    """
    try:
        # Parse request data
        data = request.json
        
        # Validate input
        is_valid, error_message = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Extract validated data
        paper_text = data.get("paper").strip()
        explanation_level = data.get("level", "college_student")
        
        # Generate analysis using Gemini
        response = model.generate_content(
            research_paper_prompt(paper_text, explanation_level)
        )
        
        # Return successful response
        return jsonify({
            "result": response.text,
            "level": LEVEL_DISPLAY_NAMES.get(explanation_level, "College Student")
        }), 200
        
    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Error analyzing research paper: {str(e)}")
        
        # Return user-friendly error message
        return jsonify({
            "error": "An error occurred while analyzing the paper. Please try again."
        }), 500


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    # Server configuration
    HOST = "127.0.0.1"
    PORT = 8000
    URL = f"http://{HOST}:{PORT}"
    
    # Auto-open browser after a short delay to allow server startup
    threading.Timer(1.0, lambda: webbrowser.open(URL)).start()
    
    # Run the Flask application
    # use_reloader=False prevents duplicate browser opening during debug
    app.run(host=HOST, port=PORT, debug=True, use_reloader=False)
