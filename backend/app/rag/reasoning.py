"""
AgentReasoner — the single reasoning interface for all agents.

Routes between:
  - Template-based reasoning (current, LANGFLOW_ENABLED=false)
  - Langflow LLM reasoning (future, LANGFLOW_ENABLED=true)

This is the Phase 3 seam. Changing config.LANGFLOW_ENABLED swaps the backend
without touching the orchestrator or any other call site.

TODO: Langflow — activate by setting LANGFLOW_ENABLED=true and implementing
      LangflowClient.run_workflow("agent_reasoning", ...) in langflow_client.py.
"""

from dataclasses import dataclass, field
from app.agents.agent_config import AgentConfig
from app.data.evidence import EvidenceItem
from app.core.config import config


@dataclass
class ReasoningResult:
    """
    Structured output from the reasoning layer.
    Consumed by the orchestrator to log trades and broadcast to the frontend.
    """
    reasoning: str                        # human-readable explanation
    conviction: str                       # "high" | "moderate" | "low"
    key_evidence: list[EvidenceItem] = field(default_factory=list)  # top evidence refs


class AgentReasoner:
    """
    Generates trade reasoning for an agent given its evidence and trade decision.

    Template mode (default, LANGFLOW_ENABLED=false):
        Calls app.agents.reasoning.template_reason() — fast, deterministic, no LLM.

    Langflow mode (LANGFLOW_ENABLED=true):
        TODO: Langflow — calls LangflowClient.run_workflow("agent_reasoning", ...)
        The workflow receives agent context, evidence, and market state, and returns
        LLM-generated reasoning with cited evidence.
    """

    def reason(
        self,
        agent: AgentConfig,
        evidence: list[EvidenceItem],
        market_price: float,
        region_id: str,
        private_belief: float,
        direction: str,
        trade_size: float,
    ) -> ReasoningResult:
        """
        Generate a reasoning explanation for an agent's trade decision.

        Args:
            agent:          Agent configuration (id, name, type, traits)
            evidence:       Evidence items the agent is basing its belief on
            market_price:   Current market probability
            region_id:      Active region identifier
            private_belief: Agent's internal probability estimate
            direction:      "BUY" or "SELL"
            trade_size:     Size of the trade being explained

        Returns:
            ReasoningResult with reasoning string and conviction label.
        """
        if config.LANGFLOW_ENABLED:
            return self._langflow_reason(
                agent, evidence, market_price, region_id,
                private_belief, direction, trade_size
            )
        return self._template_reason(
            agent, evidence, market_price, private_belief, direction, trade_size
        )

    def _template_reason(
        self,
        agent: AgentConfig,
        evidence: list[EvidenceItem],
        market_price: float,
        private_belief: float,
        direction: str,
        trade_size: float,
    ) -> ReasoningResult:
        """Template-based reasoning — current production path."""
        from app.agents.reasoning import template_reason, _conviction

        reasoning_text = template_reason(
            agent=agent,
            evidence_used=evidence,
            private_belief=private_belief,
            market_price=market_price,
            direction=direction,
            trade_size=trade_size,
        )

        gap = abs(private_belief - market_price)
        conviction_label = _conviction(gap, agent.confidence, agent.stubbornness)
        key_evidence = sorted(evidence, key=lambda e: e["strength"], reverse=True)[:3]

        return ReasoningResult(
            reasoning=reasoning_text,
            conviction=conviction_label,
            key_evidence=key_evidence,
        )

    def _langflow_reason(
        self,
        agent: AgentConfig,
        evidence: list[EvidenceItem],
        market_price: float,
        region_id: str,
        private_belief: float,
        direction: str,
        trade_size: float,
    ) -> ReasoningResult:
        """
        LLM-powered reasoning via Langflow.

        TODO: Langflow — implement this path:
            1. Build inputs dict from agent + evidence + market context
            2. Call langflow_client.run_workflow("agent_reasoning", inputs)
            3. Parse output into ReasoningResult
        """
        from app.rag.langflow_client import langflow_client

        # TODO: Langflow — replace with real implementation
        inputs = {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "agent_type": agent.agent_type,
            "categories": agent.categories,
            "evidence": [
                {
                    "id": e["id"],
                    "category": e["category"],
                    "title": e["title"],
                    "summary": e["summary"],
                    "sentiment": e["sentiment"],
                    "strength": e["strength"],
                }
                for e in evidence
            ],
            "market_price": market_price,
            "region_id": region_id,
            "private_belief": private_belief,
            "direction": direction,
            "trade_size": trade_size,
        }

        # TODO: Langflow — parse the actual workflow output shape
        result = langflow_client.run_workflow(
            config.LANGFLOW_WORKFLOW_AGENT_REASONING, inputs
        )

        return ReasoningResult(
            reasoning=result.get("reasoning", "No reasoning returned by Langflow."),
            conviction=result.get("conviction", "moderate"),
            key_evidence=evidence[:3],
        )


# Module-level singleton — import and call directly
agent_reasoner = AgentReasoner()
