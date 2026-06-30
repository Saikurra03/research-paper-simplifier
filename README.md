# 🧪 AI Research Paper Simplifier

An intelligent, stateless web application engineered to parse dense academic research papers and generate 25 structured, educational sections using zero-shot prompt engineering with Google Gemini 2.5 Flash.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-REST_Single_Page-green)

---

## 🎯 The Core Problem

Standard LLM summarization often fails in academic contexts because models tend to **hallucinate** data not present in the text or provide generic overviews that miss micro-details. Students and researchers need a tool that extracts _exact_ methodologies, generates _testable_ knowledge (MCQs, flashcards), and adapts the complexity based on the reader's academic level without inventing information.

## ⚙️ Architectural Deep-Dive

This project bypasses heavy frontend frameworks (React/Next.js) and backend ORMs in favor of a lightweight, highly efficient architecture:

1. **Stateless Backend (Flask):** Uses a single `/analyze` POST endpoint. It takes the raw text payload, injects it into a heavily engineered system prompt, and streams the response back as JSON. No session state or databases are required.
2. **Zero-Shot Prompt Engineering:** The core logic lies in `research_paper_prompt()`. The prompt is strictly bounded using delimiters and explicit negative constraints ("Do NOT invent data") to force the LLM into a constrained output format (Markdown with `##` headers).
3. **Client-Side Markdown Parsing:** Instead of adding a Python dependency like `markdown` or `flask-markdown`, the frontend JavaScript handles the parsing. It uses regex to split the API response by `##` headers and dynamically generates collapsible HTML cards. This reduces server CPU load.
4. **CORS Integration:** Flask-CORS handles cross-origin requests seamlessly, allowing the frontend to be easily migrated to a separate domain or CDN later if needed.

## 🔑 Key Technical Decisions

- **Why `gemini-2.5-flash`?** While Pro models offer deeper reasoning, Flash provides sub-10-second latency for 25 complex sections, which is critical for real-time UI feedback. The prompt is engineered to compensate for Flash's lighter reasoning by providing strict structural guidelines.
- **Why Vanilla JS instead of React?** Since the app consists of a single input form and a dynamic results container, a virtual DOM is unnecessary. Vanilla JS keeps the bundle size at 0 KB and eliminates build steps (no Webpack/Vite required).
- **Why no Database?** Research papers can contain sensitive, unpublished data. By keeping the application completely stateless and processing text in-memory, we ensure zero data retention and maximum user privacy.

## ✨ Key Features

- **Dynamic Complexity Scaling:** 3-tier explanation levels (School, College, Researcher) handled entirely via prompt context switching.
- **Structured Output Generation:** Automatically generates ELI10 explanations, step-by-step methodologies, MCQs, Viva questions, and Future Research ideas.
- **Collapsible UI Architecture:** Frontend parses Markdown headers into isolated DOM components, preventing UI lag on long texts.
- **Anti-Hallucination Guardrails:** Strict prompt constraints ensure the model explicitly outputs "Not mentioned in the paper" rather than guessing.

## 🛠️ Tech Stack

| Layer            | Technology              | Purpose                             |
| :--------------- | :---------------------- | :---------------------------------- |
| **Backend**      | Python 3.12, Flask 3.0  | REST API routing & request handling |
| **AI Engine**    | Google Generative AI    | `gemini-2.5-flash` model inference  |
| **Cross-Origin** | Flask-CORS 4.0          | Local development API bridging      |
| **Frontend**     | HTML5, CSS3, Vanilla JS | UI rendering & client-side parsing  |

## 🚀 Local Setup & Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/research-paper-simplifier.git
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
   Open `app.py` and replace the placeholder inside `genai.configure()` with your Google Gemini API key.

5. **Run the application:**
   ```bash
   python app.py
   ```
   The server will start on port 8000 and automatically open in your default browser.

## 📂 Project Structure

```text
.
├── .gitignore          # Prevents venv/cache/secret files from being tracked
├── README.md           # Architectural documentation and setup guide
├── requirements.txt    # Pinned Python dependencies
├── app.py              # Flask server, API route, and Prompt Engineering logic
└── index.html          # Single-page UI, CSS styling, and Markdown parser
```

## 📄 License

This project is licensed under the MIT License.

```

**Reply "SAVED" once you have pasted this into VS Code and pressed Ctrl+S.** Then we will do the Git push!
```
