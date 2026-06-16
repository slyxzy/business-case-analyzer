"""agent.py
Provider-agnostic adapter for sending context+question to an LLM.

This module supports multiple providers and falls back to a safe
``mock`` responder when no API keys are available so you can test
the pipeline locally without credits.
"""
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict

load_dotenv()

SYSTEM_PROMPT = """You are a senior business analyst assistant for the Government of Alberta.
You answer questions strictly based on the provided document context and reviewer comments.
If the answer cannot be found in the context, say so clearly — do not make things up.
When referencing information, mention which document it came from.
Keep answers concise, professional, and structured."""


# Optional provider SDKs
try:
    import anthropic
    _HAS_ANTHROPIC = True
except Exception:
    _HAS_ANTHROPIC = False

try:
    import openai
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False


def _mock_response(question: str, doc_context: str, comments_context: str) -> str:
    """Return a deterministic mock response useful for local testing."""
    doc_len = len(doc_context or "")
    comments_len = len(comments_context or "")
    snippet = (doc_context or "")[:800]
    return (
        "[MOCK ANSWER] No LLM provider configured. This is a local mock.\n\n"
        f"Question: {question}\n"
        f"Document context length: {doc_len} chars\n"
        f"Comments context length: {comments_len} chars\n\n"
        "Context snippet:\n"
        f"{snippet}\n\n"
        "To enable real LLM responses, set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env."
    )


def _ask_anthropic(question: str, doc_context: str, comments_context: str, chat_history: Optional[List[Dict]] = None) -> str:
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
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def _ask_openai(question: str, doc_context: str, comments_context: str, chat_history: Optional[List[Dict]] = None) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    system = {"role": "system", "content": SYSTEM_PROMPT}
    user_content = f"""DOCUMENT CONTEXT:
{doc_context}

REVIEWER COMMENTS:
{comments_context}

QUESTION: {question}"""

    messages = [system]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_content})

    resp = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        max_tokens=1500,
    )
    return resp["choices"][0]["message"]["content"]


def ask_agent(question: str, doc_context: str, comments_context: str, chat_history: Optional[List[Dict]] = None) -> str:
    """Public API used by the app: routes the call to an available provider.

    Priority: ANTHROPIC_API_KEY -> OPENAI_API_KEY -> mock fallback.
    """
    if os.getenv("ANTHROPIC_API_KEY") and _HAS_ANTHROPIC:
        try:
            return _ask_anthropic(question, doc_context, comments_context, chat_history)
        except Exception as e:
            print(f"Anthropic request failed: {e}")

    if os.getenv("OPENAI_API_KEY") and _HAS_OPENAI:
        try:
            return _ask_openai(question, doc_context, comments_context, chat_history)
        except Exception as e:
            print(f"OpenAI request failed: {e}")

    return _mock_response(question, doc_context, comments_context)


def get_summary(doc_context: str, comments_context: str) -> str:
    """Generate a short summary using the same provider selection as ask_agent.

    The mock summary is concise and suitable for UI testing.
    """
    prompt = (
        "Provide a structured summary covering:\n"
        "- Program/initiative overview\n"
        "- Key objectives\n"
        "- Budget or resource implications\n"
        "- Main concerns raised by reviewers\n"
    )
    return ask_agent(prompt, doc_context, comments_context)
