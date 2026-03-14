"""
AI pipeline router — single-agent run + orchestrated prediction pipeline.
"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.ai.pipeline import run_pipeline
from app.ai.orchestrator import run_phase1, run_phase1_stream, run_orchestrated_phase2, run_phase2_stream
from app.ai.rag import add_documents
from app.ai.schemas import (
    RunRequest,
    RunResponse,
    ContextRunRequest,
    ContextRunResponse,
    Phase1Request,
    Phase1Response,
    Phase2Request,
    Phase2Response,
    IngestRequest,
    IngestResponse,
)
from app.agents.config import list_agents

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/agents")
def agents():
    """List configured agents (id, name, description)."""
    return {
        "agents": [
            {"id": a.id, "name": a.name, "description": a.description, "model": a.model}
            for a in list_agents()
        ]
    }


@router.post("/run", response_model=RunResponse)
def run(request: RunRequest):
    """Run a single-agent pipeline: RAG (optional) + system prompt + LLM. No additional context."""
    response = run_pipeline(
        message=request.message,
        system_prompt=request.system_prompt,
        agent_id=request.agent_id,
        use_rag=request.use_rag,
        model=request.model,
    )
    return RunResponse(response=response)


@router.post("/contextrun", response_model=ContextRunResponse)
def contextrun(request: ContextRunRequest):
    """Run the same agent pipeline with optional additional context (e.g. orchestrator-assigned RAG)."""
    response = run_pipeline(
        message=request.message,
        system_prompt=request.system_prompt,
        agent_id=request.agent_id,
        use_rag=request.use_rag,
        model=request.model,
        additional_context=request.additional_context,
    )
    return ContextRunResponse(response=response)


@router.post("/phase1", response_model=Phase1Response)
def phase1(request: Phase1Request):
    """
    Phase 1: Same as /run but runs every agent with /run.
    Optional RAG, then run_pipeline per agent; web scrape. Returns initial_bets + rag_context for phase2.
    """
    result = run_phase1(
        question=request.question,
        use_rag=request.use_rag,
        model=request.model,
    )
    return Phase1Response(**result)


def _phase1_sse_generator(request: Phase1Request):
    """Yield SSE-formatted lines for phase1 stream."""
    for payload in run_phase1_stream(
        question=request.question,
        use_rag=request.use_rag,
        model=request.model,
    ):
        event_type = payload.get("event", "message")
        data = json.dumps(payload)
        yield f"event: {event_type}\ndata: {data}\n\n"


@router.post("/phase1/stream")
def phase1_stream(request: Phase1Request):
    """
    Phase 1 as Server-Sent Events: agents run in parallel; one event per agent when done,
    then a final phase1_complete event with the full result.
    """
    return StreamingResponse(
        _phase1_sse_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/phase2", response_model=Phase2Response)
def phase2(request: Phase2Request):
    """
    Phase 2: Orchestrator reads RAG context and initiates agents with new context.
    Relevant agents make a second bet; assigned agent runs deep analysis.
    """
    bets = [b.model_dump() for b in request.initial_bets]

    phase2_result = run_orchestrated_phase2(
        question=request.question,
        initial_bets=bets,
        web_scrape_snippets=request.web_scrape_snippets,
        rag_context=request.rag_context,
        rag_chunks=request.rag_chunks or None,
        question_prompt=request.question_prompt or None,
        model=request.model,
    )

    return Phase2Response(
        question=request.question,
        initial_bets=request.initial_bets,
        web_scrape_snippets=request.web_scrape_snippets,
        rag_context=request.rag_context,
        rag_chunks=request.rag_chunks,
        **phase2_result,
    )


def _phase2_sse_generator(request: Phase2Request):
    """Yield SSE-formatted lines for phase2 stream."""
    bets = [b.model_dump() for b in request.initial_bets]
    for payload in run_phase2_stream(
        question=request.question,
        initial_bets=bets,
        web_scrape_snippets=request.web_scrape_snippets,
        rag_context=request.rag_context,
        rag_chunks=request.rag_chunks or None,
        question_prompt=request.question_prompt or None,
        model=request.model,
    ):
        event_type = payload.get("event", "message")
        data = json.dumps(payload)
        yield f"event: {event_type}\ndata: {data}\n\n"


@router.post("/phase2/stream")
def phase2_stream(request: Phase2Request):
    """
    Phase 2 as Server-Sent Events: orchestrator_done, then one agent_second_bet_done per
    relevant agent (parallel), then deep_analysis_done, then phase2_complete with full result.
    """
    return StreamingResponse(
        _phase2_sse_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    """Ingest documents into the vector store."""
    add_documents(
        texts=request.texts,
        ids=request.ids,
        collection_name=request.collection_name,
    )
    return IngestResponse(
        count=len(request.texts),
        message=f"Successfully ingested {len(request.texts)} documents into '{request.collection_name}'.",
    )

