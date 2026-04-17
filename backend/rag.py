"""
Vishnu Gita - RAG Pipeline
Retrieves relevant scripture passages and generates wise answers
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from prompts import DIVINE_SYSTEM_PROMPT

DB_DIR = os.path.join(os.path.dirname(__file__), "divine_db")

# Initialize once at startup
_client = None
_collection = None
_groq = None


def init():
    global _client, _collection, _groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env file")

    _groq = Groq(api_key=api_key)

    if not os.path.exists(DB_DIR):
        raise FileNotFoundError(
            "Database not found! Run: cd data && python build_database.py"
        )

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    _client = chromadb.PersistentClient(path=DB_DIR)
    _collection = _client.get_collection("scriptures", embedding_function=embed_fn)
    print(f"  Vishnu Gita RAG ready. {_collection.count()} passages loaded.")


def ask(question: str, chat_history: list = None) -> dict:
    """
    Main function: takes a question, finds relevant scriptures, returns answer.
    Returns: { "answer": str, "sources": list }
    """
    if _collection is None:
        init()

    # 1. Find top 5 relevant scripture passages (safely)
    n = min(5, _collection.count())
    results = _collection.query(
        query_texts=[question],
        n_results=n
    )

    passages = results["documents"][0]
    metas = results["metadatas"][0]

    # 2. Build context string
    context = ""
    sources = []
    for i, (text, meta) in enumerate(zip(passages, metas)):
        label = f"{meta.get('source', '')} - {meta.get('parva', '')} {meta.get('section', '')}".strip(" -")
        context += f"\n[{i+1}] {label}:\n{text}\n"
        sources.append(label)

    # 3. Build messages
    messages = [{"role": "system", "content": DIVINE_SYSTEM_PROMPT}]

    # Add chat history if provided (last 4 exchanges)
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

    # Hard trim to ~130 words max (keeps last sentence complete)
    words = answer.split()
    if len(words) > 130:
        trimmed = ' '.join(words[:130])
        # Find the last sentence-ending punctuation to not cut mid-sentence
        for end in ['. ', '.\n', '! ', '? ']:
            last = trimmed.rfind(end)
            if last > 60:
                trimmed = trimmed[:last + 1]
                break
        answer = trimmed

    return {
        "answer": answer,
        "sources": list(set(sources))  # Deduplicated sources
    }
