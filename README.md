# AI Research Paper Simplifier

An intelligent web application that parses dense academic research papers and generates 25 structured, educational sections using the Cohere API. Supports PDF upload with automatic text extraction.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![Cohere](https://img.shields.io/badge/Cohere-Command%20A-39594D?logo=cohere&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## The Core Problem

Standard LLM summarization often fails in academic contexts because models tend to **hallucinate** data not present in the text or provide generic overviews that miss micro-details. Students and researchers need a tool that extracts _exact_ methodologies, generates _testable_ knowledge (MCQs, flashcards), and adapts the complexity based on the reader's academic level without inventing information.

## Key Features

- **PDF Upload** - Drag and drop PDF research papers, text extracted automatically using PyMuPDF
- **25 Structured Sections** - From ELI10 explanations to technical deep-dives, methodology breakdowns, and research gaps
- **3 Explanation Levels** - School Student, College Student, and Researcher modes
- **Study Tools** - Auto-generated flashcards, MCQs, viva questions, and interview prep
- **Multi-Page SPA** - Home, Analyze, and About pages with smooth navigation
- **Polished UI** - Glassmorphism navbar, animated cards, gradient accents, responsive design
- **Collapsible Sections** - Expand/collapse individual sections, expand all, copy to clipboard
- **Anti-Hallucination Guardrails** - Strict prompt constraints ensure the model outputs "Not mentioned in the paper" rather than guessing

## Tech Stack

| Layer        | Technology                  | Purpose                             |
|:-------------|:----------------------------|:------------------------------------|
| **Backend**  | Python 3.12, Flask          | REST API routing & request handling |
| **AI Engine**| Cohere Command A API        | LLM inference via `/v2/chat`        |
| **PDF**      | PyMuPDF (fitz)              | PDF text extraction                 |
| **Frontend** | HTML5, CSS3, Vanilla JS     | SPA with collapsible card UI        |
| **Hosting**  | Render.com                  | Free tier with auto-deploy          |

## Local Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Saikurra03/research-paper-simplifier.git
   cd research-paper-simplifier
   ```

2. **Create and activate a virtual environment:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key:**

   Create a `.env` file in the project root:

   ```
   COHERE_API_KEY=your-api-key-here
   ```

   Get your free API key from https://dashboard.cohere.com/api-keys

5. **Run the application:**

   ```bash
   python app.py
   ```

   The server will start on port 8000 and open in your browser.

## Project Structure

```
.
├── .gitignore          # Prevents venv/.env/cache from being tracked
├── .env                # API key (not committed)
├── render.yaml         # Render deployment config
├── requirements.txt    # Python dependencies
├── app.py              # Flask server, API routes, Cohere integration
├── index.html          # SPA frontend with multi-page navigation
└── README.md           # This file
```

## API Endpoints

| Method | Endpoint       | Description                        |
|:-------|:---------------|:-----------------------------------|
| GET    | `/`            | Serve the SPA frontend             |
| POST   | `/api/upload`  | Extract text from uploaded PDF     |
| POST   | `/api/analyze` | Analyze paper and return 25 sections |
| GET    | `/api/models`  | List available AI models           |

## Deployment to Render

1. Push your code to GitHub
2. Go to https://dashboard.render.com and sign up with GitHub
3. Click **New +** > **Web Service**
4. Connect your repository
5. Set environment variable: `COHERE_API_KEY` = your key
6. Click **Create Web Service**

Your app will be live at `https://your-app-name.onrender.com`.

## License

MIT License
