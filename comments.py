"""
comments.py
Extracts reviewer comments and body text from .docx files.
"""
from docx import Document
from lxml import etree

WNS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_comments(filepath: str) -> list[dict]:
    """Return a list of {author, date, text} dicts from a .docx file."""
    doc = Document(filepath)
    comments = []
    try:
        comments_part = doc.part.comments_part
        if not comments_part:
            return []
        root = comments_part._element
        for comment in root.iter(f"{WNS}comment"):
            author = comment.get(f"{WNS}author", "Unknown")
            date = comment.get(f"{WNS}date", "")[:10]
            text = "".join(
                t.text for t in comment.iter(f"{WNS}t") if t.text
            ).strip()
            if text:
                comments.append({"author": author, "date": date, "text": text})
    except Exception as e:
        print(f"Warning: could not extract comments from {filepath}: {e}")
    return comments


def extract_body_text(filepath: str) -> str:
    """Return the full body text of a .docx file."""
    doc = Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def format_comments_for_llm(comments: list[dict]) -> str:
    """Format comments into a readable string for the LLM context."""
    if not comments:
        return "No reviewer comments found."
    lines = [f"[{c['date']}] {c['author']}: {c['text']}" for c in comments]
    return "\n".join(lines)