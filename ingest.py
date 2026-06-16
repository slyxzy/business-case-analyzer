"""
ingest.py
Loads PDF and DOCX files from the /docs folder,
chunks them into smaller pieces for RAG retrieval.
"""
import os
import pdfplumber
from comments import extract_body_text


def load_documents(folder: str = "./docs") -> list[dict]:
    """
    Load all .pdf and .docx files from a folder.
    Returns list of {filename, content} dicts.
    """
    docs = []
    supported = (".pdf", ".docx")
    for filename in os.listdir(folder):
        if not filename.lower().endswith(supported):
            continue
        filepath = os.path.join(folder, filename)
        content = ""
        try:
            if filename.endswith(".pdf"):
                with pdfplumber.open(filepath) as pdf:
                    content = "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
            elif filename.endswith(".docx"):
                content = extract_body_text(filepath)

            if content.strip():
                docs.append({"filename": filename, "content": content})
                print(f"  Loaded: {filename} ({len(content)} chars)")
        except Exception as e:
            print(f"  Error loading {filename}: {e}")
    return docs


def chunk_documents(docs: list[dict], chunk_size: int = 800, overlap: int = 100) -> list[dict]:
    """
    Split documents into overlapping chunks for better retrieval.
    Returns list of {filename, chunk_index, content} dicts.
    """
    chunks = []
    for doc in docs:
        text = doc["content"]
        start = 0
        idx = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "filename": doc["filename"],
                    "chunk_index": idx,
                    "content": chunk_text
                })
            start += chunk_size - overlap
            idx += 1
    print(f"  Total chunks created: {len(chunks)}")
    return chunks