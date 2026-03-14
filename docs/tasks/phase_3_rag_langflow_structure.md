# Phase 3 Tasks — RAG/Langflow Structure

## Goal
Create clean integration seams so real RAG and Langflow can be added without restructuring the codebase.

## Tasks

### B3.1 — CategoryRetriever Interface
- [ ] Create `backend/app/rag/retrieval.py`
- [ ] Define `EvidenceItem` dataclass (if not already in trade_models)
- [ ] Define `CategoryRetriever` class with `retrieve(region_id, top_k)` method
- [ ] Implement seeded backend (calls existing evidence functions)
- [ ] Add TODO: RAG comment at the vector store call site

### B3.2 — Access Control Layer
- [ ] Create `backend/app/rag/access.py`
- [ ] Function: `get_retrievers_for_agent(agent) -> list[CategoryRetriever]`
- [ ] Filters retrievers by agent.categories
- [ ] Add TODO: RAG comment for future permission enforcement

### B3.3 — AgentReasoner Interface
- [ ] Create `backend/app/rag/reasoning.py`
- [ ] Define `ReasoningResult` dataclass: `{belief: float, reasoning: str, key_evidence: list}`
- [ ] Define `AgentReasoner` class with `reason(agent, evidence, market_price, region)` method
- [ ] Implement template-based backend (uses existing templates)
- [ ] Add TODO: Langflow comment at LLM call site

### B3.4 — LangflowClient Stub
- [ ] Create `backend/app/rag/langflow_client.py`
- [ ] Define `LangflowClient` class with `run_workflow(workflow_id, inputs)` method
- [ ] Raise `NotImplementedError` with helpful message
- [ ] Add config keys to `backend/app/core/config.py`

### B3.5 — Refactor Belief Engine
- [ ] Update `backend/app/agents/belief_engine.py` to use `CategoryRetriever`
- [ ] Update `backend/app/agents/reasoning.py` to use `AgentReasoner`
- [ ] All evidence access goes through retriever interface (no direct data calls)

### B3.6 — Corpus Mapping
- [ ] Create `backend/app/rag/corpus_map.py`
- [ ] Maps category string to corpus name constant
- [ ] Documents expected corpus structure for future ingestion

## Acceptance Criteria
- [ ] All evidence access goes through `CategoryRetriever.retrieve()`
- [ ] All reasoning goes through `AgentReasoner.reason()`
- [ ] Every RAG/Langflow seam has a TODO comment
- [ ] A developer can grep `TODO: RAG` and find all integration points
- [ ] No behavior regression from Phase 2
