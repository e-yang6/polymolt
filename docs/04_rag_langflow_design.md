# RAG and Langflow Architecture Design

## Purpose

This document describes the intended retrieval-augmented generation (RAG) and Langflow integration architecture. In the MVP, all evidence is seeded. This document defines where real retrieval would plug in and how Langflow would orchestrate agent reasoning.

---

## Category Corpus Design

Each sustainability category maps to a dedicated vector corpus:

| Category | Corpus Name | Example Documents |
|----------|-------------|-------------------|
| Climate & Emissions | `climate_and_emissions` | IPCC reports, national emissions data, temperature anomaly datasets |
| Energy & Resource Systems | `energy_and_resource_systems` | IEA energy mix data, renewable capacity reports, resource depletion studies |
| Water & Ecosystems | `water_and_ecosystems` | UNEP water stress reports, biodiversity indices, deforestation data |
| Infrastructure & Built Environment | `infrastructure_and_built_environment` | Urban resilience indices, infrastructure gap reports, smart city benchmarks |
| Economy & Social Resilience | `economy_and_social_resilience` | UNDP HDI, Gini coefficient data, food security reports |
| Governance & Policy | `governance_and_policy` | ESG policy indices, NDC compliance data, corruption indices |

---

## Retrieval Layer Interface

```python
# backend/app/rag/retrieval.py
# TODO: RAG — replace mock with real vector search

class CategoryRetriever:
    """
    Retrieves evidence items for a given category and region.
    In MVP: returns seeded evidence from data/regions.py
    Future: queries a vector store (Pinecone, Chroma, Weaviate)
    """
    def __init__(self, corpus_name: str):
        self.corpus_name = corpus_name

    def retrieve(self, region_id: str, top_k: int = 5) -> list[EvidenceItem]:
        # TODO: RAG — replace with:
        # embedding = embed(f"{region_id} sustainability {self.corpus_name}")
        # results = vector_store.query(embedding, top_k=top_k, filter={"corpus": self.corpus_name})
        # return [EvidenceItem(**r) for r in results]
        return get_seeded_evidence(region_id, self.corpus_name)
```

---

## Agent-Specific Access Control

```python
# backend/app/rag/access.py
# TODO: RAG — enforce corpus-level access control

def get_retrievers_for_agent(agent: Agent) -> list[CategoryRetriever]:
    """
    Returns only the retrievers the agent is allowed to use.
    Specialists: one retriever
    Hybrids: three retrievers
    Master: all six retrievers
    """
    return [CategoryRetriever(cat) for cat in agent.categories]
```

---

## Reasoning Layer Interface

```python
# backend/app/rag/reasoning.py
# TODO: Langflow — replace with Langflow workflow call

class AgentReasoner:
    """
    Takes evidence items and produces a belief + explanation.
    In MVP: uses template-based reasoning with scored evidence
    Future: calls a Langflow workflow that runs an LLM reasoning chain
    """
    def reason(
        self,
        agent: Agent,
        evidence: list[EvidenceItem],
        market_price: float,
        region: Region
    ) -> ReasoningResult:
        # TODO: Langflow — replace with:
        # return langflow_client.run_workflow(
        #     workflow_id=f"agent_reasoning_{agent.agent_type}",
        #     inputs={
        #         "agent_id": agent.id,
        #         "evidence": [e.dict() for e in evidence],
        #         "market_price": market_price,
        #         "region": region.name
        #     }
        # )
        return template_reason(agent, evidence, market_price)
```

---

## Langflow Workflow Design

### Workflow: `agent_reasoning`

```
Input: {agent_id, evidence[], market_price, region_name}
  ↓
Evidence Formatter Node
  ↓
LLM Reasoning Node (Claude / GPT-4)
  Prompt: "You are {agent_name}. You have access to the following evidence: {evidence}.
           The current market probability is {market_price}.
           What is your belief about regional sustainability? Explain your reasoning."
  ↓
Belief Extractor Node (parse probability from LLM output)
  ↓
Explanation Formatter Node
  ↓
Output: {belief: float, reasoning: str, key_evidence: list}
```

### Workflow: `trade_decision`

```
Input: {agent, belief, market_price, position}
  ↓
Gap Calculator Node
  ↓
Trade Sizer Node (applies betting_power, confidence, risk_tolerance)
  ↓
Output: {direction: BUY|SELL, size: float, reasoning: str}
```

---

## Integration Points in Codebase

Mark every integration point with a `# TODO: RAG` or `# TODO: Langflow` comment:

```python
# In backend/app/agents/belief_engine.py:
# TODO: RAG — replace get_seeded_evidence() with CategoryRetriever.retrieve()

# In backend/app/agents/reasoning.py:
# TODO: Langflow — replace template_reason() with langflow_client.run_workflow()

# In backend/app/core/orchestrator.py:
# TODO: Langflow — replace direct agent.update() with workflow dispatch
```

---

## Corpus File Structure (Future)

```
backend/
  data/
    corpora/
      climate_and_emissions/
        ipcc_ar6_summary.txt
        co2_emissions_2023.csv
        ...
      energy_and_resource_systems/
        iea_world_energy_2023.txt
        ...
      (one directory per corpus)
```

---

## Langflow Client Stub

```python
# backend/app/rag/langflow_client.py
# TODO: Langflow — implement real client

class LangflowClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def run_workflow(self, workflow_id: str, inputs: dict) -> dict:
        # TODO: Langflow — POST to Langflow API
        raise NotImplementedError("Langflow integration not yet implemented")
```
