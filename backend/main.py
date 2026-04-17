"""
Vishnu Gita - FastAPI Backend
Serves the chat API for both the website and WhatsApp
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n Starting Vishnu Gita...")
    db_path = os.path.join(os.path.dirname(__file__), "divine_db")
    if not os.path.exists(db_path):
        print(" Database not found — building it now (takes ~3 mins)...")
        import subprocess, sys
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        subprocess.run([sys.executable, "download_data.py"], cwd=data_dir, check=True)
        subprocess.run([sys.executable, "build_database.py"], cwd=data_dir, check=True)
        print(" Database built!")
    rag.init()
    print(" Vishnu Gita is ready!\n")
    yield


app = FastAPI(title="Vishnu Gita API", lifespan=lifespan)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend website
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]



@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Vishnu Gita"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    history = [{"role": m.role, "content": m.content} for m in req.history]

    result = rag.ask(req.question, chat_history=history)

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  Vishnu Gita is starting...")
    print("  Website: http://localhost:8000")
    print("  API:     http://localhost:8000/chat")
    print("=" * 60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
