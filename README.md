# 📄 Business Case Analyzer

An AI-powered document analysis tool that extracts reviewer comments from Word documents and lets you chat with business case PDFs and DOCX files using RAG (Retrieval-Augmented Generation).

## Features

- **Extract Word Comments** — Automatically reads colleague comments from `.docx` files
- **RAG-Powered Chat** — Ask questions about your documents and get grounded answers
- **Summary Generation** — Auto-generate executive summaries of business cases
- **Multi-Document Support** — Analyze PDFs and Word documents together
- **No API Keys Required** — Comes with a mock LLM for testing; add your own API key to enable real responses

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

Open your browser to **http://localhost:8501**

### 3. Upload & Analyze

1. Drop `.docx` or `.pdf` files in the sidebar
2. Click **🔍 Analyze Documents**
3. View extracted comments and the AI summary
4. Chat with your documents in the 💬 Chat tab

## Configure an LLM Provider

The app works without API keys (using mock responses), but to enable real AI responses:

### Anthropic (Claude)

```bash
# Get a free key at https://console.anthropic.com
# Create a .env file in the project root:
ANTHROPIC_API_KEY=your_key_here
```

### OpenAI (GPT)

```bash
# Set up your OpenAI API key in .env:
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

The app will auto-detect your keys and use the first available provider.

## What It Does

### Comment Extraction

Reads colleague feedback directly from Word documents:
- Author name
- Date of comment
- Comment text

### RAG Pipeline

1. **Chunk** — Splits documents into ~800-char chunks
2. **Embed** — Converts chunks to vectors (local embeddings)
3. **Index** — Stores vectors in ChromaDB
4. **Retrieve** — Finds top 4 relevant chunks for your question
5. **Generate** — Sends chunks + question to the LLM

## Files

- `app.py` — Streamlit UI
- `comments.py` — Extract comments and body text from DOCX
- `ingest.py` — Load and chunk PDFs and DOCX files
- `rag.py` — Build vector index and retrieve
- `agent.py` — LLM interface (supports Anthropic, OpenAI, or mock)

## Troubleshooting

**"No reviewer comments were extracted"**
- Ensure your Word doc has comments (Insert > Comment in Word)
- The app reads comments stored in the `word/comments.xml` part of the DOCX

**Mock answers appearing instead of real AI**
- Set an `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`
- Restart Streamlit (`Ctrl+C`, then `streamlit run app.py`)

## License

MIT
