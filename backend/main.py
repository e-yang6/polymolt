"""
PolyMolt backend — FastAPI app. Run the RAG + agent pipeline when you hit the route.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import run_pipeline
from app.agents.config import list_agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PolyMolt API",
    description="RAG + specialized system-prompt agents; run the pipeline via POST /run",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    message: str
    system_prompt: str | None = None
    agent_type: str | None = None  # e.g. "climate", "policy", "regional" → predefined system prompts
    use_rag: bool = True
    model: str | None = None  # override LLM for this request (e.g. "gpt-4o", "gpt-4-turbo")


class RunResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {"name": "PolyMolt API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/agents")
def agents():
    """List configured agents (id, name, description). Use agent_type=id in POST /run."""
    return {
        "agents": [
            {"id": a.id, "name": a.name, "description": a.description, "model": a.model}
            for a in list_agents()
        ]
    }


@app.post("/run", response_model=RunResponse)
def run(request: RunRequest):
    """
    Run the pipeline: RAG (optional) + specialized system prompt + LLM.
    Pipeline runs when you call this route.
    """
    response = run_pipeline(
        message=request.message,
        system_prompt=request.system_prompt,
        agent_type=request.agent_type,
        use_rag=request.use_rag,
        model=request.model,
    )
    return RunResponse(response=response)
