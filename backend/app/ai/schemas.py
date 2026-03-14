from __future__ import annotations

from pydantic import BaseModel


# ── Single-agent run (kept for backwards compat) ──

class RunRequest(BaseModel):
    message: str
    system_prompt: str | None = None
    agent_id: str | None = None
    use_rag: bool = True
    model: str | None = None


class RunResponse(BaseModel):
    response: str


class ContextRunRequest(BaseModel):
    """Same as RunRequest plus optional additional context passed into the run."""
    message: str
    system_prompt: str | None = None
    agent_id: str | None = None
    use_rag: bool = True
    model: str | None = None
    additional_context: str | None = None


class ContextRunResponse(BaseModel):
    response: str


# ── Phase 1 / Phase 2 (orchestrated pipeline) ──


class AgentBet(BaseModel):
    agent_id: str
    agent_name: str
    answer: str          # "YES" or "NO"
    confidence: int      # 0-100
    reasoning: str


class Phase1Request(BaseModel):
    question: str
    use_rag: bool = True
    model: str | None = None


class Phase1Response(BaseModel):
    question: str
    initial_bets: list[AgentBet]
    web_scrape_snippets: list[str]
    rag_context: str
    rag_chunks: list[str] = []


class AgentRagAssignment(BaseModel):
    agent_id: str
    rag_context_for_agent: str


class Phase2Request(Phase1Response):
    question_prompt: str = "[Placeholder: question prompt for the prediction market]"
    model: str | None = None


class Phase2Response(Phase1Response):
    assigned_agent_id: str
    assigned_agent_name: str
    expertise_rationale: str
    relevant_agents_with_rag: list[AgentRagAssignment] = []
    second_bets: list[AgentBet] = []  # relevant agents' second bet after orchestrator assignment
    deep_analysis: str


# ── RAG Ingestion ──

class IngestRequest(BaseModel):
    texts: list[str]
    ids: list[str] | None = None
    collection_name: str = "rag"


class IngestResponse(BaseModel):
    count: int
    message: str

