"""
agent.py
Sends the retrieved context + user question to Claude
and returns a grounded answer. This is the "generation"
step in Retrieval-Augmented Generation (RAG).
"""
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior business analyst assistant for the Government of Alberta.
You answer questions strictly based on the provided document context and reviewer comments.
If the answer cannot be found in the context, say so clearly — do not make things up.
When referencing information, mention which document it came from.
Keep answers concise, professional, and structured."""


def ask_agent(question: str, doc_context: str, comments_context: str, chat_history: list[dict] = None) -> str:
    """Send question + context to Claude and return the response."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    user_content = f"""DOCUMENT CONTEXT:
{doc_context}

REVIEWER COMMENTS:
{comments_context}

QUESTION: {question}"""

    messages = []
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_content})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text


def get_summary(doc_context: str, comments_context: str) -> str:
    """Generate a quick summary of the uploaded business case."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""DOCUMENT CONTEXT:
{doc_context}

REVIEWER COMMENTS:
{comments_context}

Provide a structured summary covering:
- Program/initiative overview
- Key objectives
- Budget or resource implications
- Main concerns raised by reviewers"""
        }]
    )
    return response.content[0].text