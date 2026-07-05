# Research Paper Simplifier

Paste a research paper or upload a PDF and get a clean breakdown of everything in it - explained simply, with flashcards, MCQs, and interview questions ready to study.

## What it does

You paste in a research paper (or upload a PDF), pick who it's explained for (school student, college student, or researcher), and it gives you 25 organized sections covering:

- Simple explanations at your level
- Problem statement and why the research matters
- Methodology step by step
- Key contributions, advantages, limitations
- Flashcards and MCQs for studying
- Viva and interview questions
- Future research ideas

## How to run it on your computer

**Step 1:** Download the code
```
git clone https://github.com/Saikurra03/research-paper-simplifier.git
cd research-paper-simplifier
```

**Step 2:** Make a virtual environment
```
python -m venv venv
venv\Scripts\activate
```

**Step 3:** Install the stuff it needs
```
pip install -r requirements.txt
```

**Step 4:** Get a free API key
- Go to https://dashboard.cohere.com/api-keys
- Sign up and create a key
- Copy it

**Step 5:** Create a `.env` file in the project folder and paste your key
```
COHERE_API_KEY=paste-your-key-here
```

**Step 6:** Run it
```
python app.py
```

It'll open in your browser at http://127.0.0.1:8000

## How to put it online (free)

1. Push your code to GitHub
2. Go to https://render.com and sign up with GitHub
3. Click New + > Web Service
4. Pick your repo
5. In Environment, add: `COHERE_API_KEY` = your key
6. Click Create Web Service

Wait a couple minutes and you'll have a live link.

## What it's built with

- **Python + Flask** - backend
- **Cohere API** - the AI that reads and explains papers
- **PyMuPDF** - reads text from PDF files
- **HTML/CSS/JS** - the frontend (no frameworks, just plain code)

## Files

- `app.py` - the main server code
- `index.html` - the website frontend
- `.env` - your API key (don't share this)
- `requirements.txt` - list of packages to install
- `render.yaml` - deployment config for Render

## License

Do whatever you want with it.
