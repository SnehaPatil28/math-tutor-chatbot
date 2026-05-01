"""
groq_client.py — Groq API wrapper.
The API key and model are read from Streamlit secrets (cloud) or .env (local).
Never exposed to the UI.
"""

import os
import streamlit as st

def _get(key: str, default: str = "") -> str:
    """Read from st.secrets first, fall back to env var."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)

from groq import Groq

# ── Client (singleton) ────────────────────────────────────────
_client = Groq(api_key=_get("GROQ_API_KEY"))
MODEL   = _get("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── System prompt: E01 Basic Prompting + E02 Chain-of-Thought ─
SYSTEM_PROMPT = """You are an expert math tutor. Your job is to help students understand mathematics deeply — not just get answers.

STRICT RESPONSE FORMAT — always follow this exact structure:

1. BRIEF INTRO: One sentence identifying what type of problem this is.

2. STEP-BY-STEP SOLUTION: Number every step. For each step:
   - State clearly what you are doing
   - Show the full math work
   - Explain WHY this step is necessary or valid

3. FINAL ANSWER: Clearly state the final answer on its own line, prefixed exactly with:
   FINAL ANSWER: <answer here>

4. PRO TIP: End with one practical tip, trick, or insight related to this type of problem, prefixed exactly with:
   PRO TIP: <tip here>

Rules:
- Never skip steps. Show all work.
- Use plain text math notation (e.g., x^2, sqrt(x), pi).
- If the user asks a follow-up (like "explain step 2 again"), refer back to the previous solution and re-explain clearly.
- If the input is not a math question, politely redirect the user to ask a math question.
"""


def chat(messages: list[dict]) -> str:
    """
    Send a conversation history to Groq and return the assistant reply.
    messages = [{"role": "user"|"assistant", "content": "..."}]
    """
    completion = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        temperature=0.4,
        max_tokens=1200,
    )
    return completion.choices[0].message.content
