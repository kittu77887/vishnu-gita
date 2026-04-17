"""
Vishnu Gita - RAG Pipeline (Lightweight TF-IDF version)
Uses scikit-learn TF-IDF instead of sentence-transformers — fits in 512MB RAM
"""

import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from prompts import DIVINE_SYSTEM_PROMPT

# Global state
_passages = []
_vectorizer = None
_matrix = None
_groq = None


def _load_passages():
    """Load all scripture JSON files"""
    passages = []
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    for fname in ["mahabharata.json", "bhagavad_gita.json"]:
        fpath = os.path.join(raw_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            passages.extend(data)
            print(f"  Loaded {len(data)} passages from {fname}")
    return passages


def init():
    global _passages, _vectorizer, _matrix, _groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    _groq = Groq(api_key=api_key)

    print("  Loading scripture passages...")
    _passages = _load_passages()
    if not _passages:
        raise FileNotFoundError("No scripture data found in data/raw/")

    print(f"  Building TF-IDF index over {len(_passages)} passages...")
    texts = [p.get("text", "") for p in _passages]
    _vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=8000,
        ngram_range=(1, 2)
    )
    _matrix = _vectorizer.fit_transform(texts)
    print(f"  Vishnu Gita RAG ready. {len(_passages)} passages indexed.")


def _search(query: str, n: int = 5):
    """Find top-n most relevant passages for a query"""
    q_vec = _vectorizer.transform([query])
    scores = cosine_similarity(q_vec, _matrix)[0]
    top_indices = np.argsort(scores)[-n:][::-1]
    return [_passages[i] for i in top_indices if scores[i] > 0]


def ask(question: str, chat_history: list = None) -> dict:
    """
    Main function: finds relevant scriptures, returns a simple answer.
    Returns: { "answer": str, "sources": list }
    """
    if _vectorizer is None:
        init()

    # 1. Find relevant passages
    results = _search(question, n=5)
    if not results:
        results = _passages[:3]  # fallback to first 3

    # 2. Build context
    context = ""
    sources = []
    for i, p in enumerate(results):
        label = f"{p.get('source', '')} - {p.get('parva', '')} {p.get('section', '')}".strip(" -")
        context += f"\n[{i+1}] {label}:\n{p.get('text', '')}\n"
        sources.append(label)

    # 3. Build messages
    messages = [{"role": "system", "content": DIVINE_SYSTEM_PROMPT}]
    if chat_history:
        for msg in chat_history[-8:]:
            messages.append(msg)

    messages.append({
        "role": "user",
        "content": f"""Scripture passages to use:
{context}

Question: {question}

IMPORTANT: Reply in 4 short parts only — no headers, no bold labels:
1) One simple lesson from scripture (1 sentence)
2) One short story/example (2 sentences)
3) What to do (3 bullet points starting with •)
4) One closing sentence

Total reply must be under 120 words. Plain simple language only."""
    })

    # 4. Call Groq
    response = _groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.6,
        max_tokens=300
    )

    answer = response.choices[0].message.content.strip()

    # Hard trim to ~130 words max
    words = answer.split()
    if len(words) > 130:
        trimmed = ' '.join(words[:130])
        for end in ['. ', '.\n', '! ', '? ']:
            last = trimmed.rfind(end)
            if last > 60:
                trimmed = trimmed[:last + 1]
                break
        answer = trimmed

    return {
        "answer": answer,
        "sources": list(dict.fromkeys(sources))  # deduplicated, order preserved
    }
