"""
Langflow client stub.

When LANGFLOW_ENABLED=true, AgentReasoner will call this client instead of
using template-based reasoning.

To activate:
  1. Deploy Langflow locally: `pip install langflow && langflow run`
  2. Import the workflow JSON from docs/langflow/ (to be created)
  3. Set LANGFLOW_ENABLED=true, LANGFLOW_BASE_URL, LANGFLOW_API_KEY

TODO: Langflow — implement run_workflow() once Langflow is deployed.
"""

import logging
from app.core.config import config

logger = logging.getLogger(__name__)


class LangflowClient:
    """
    Client for running Langflow workflows.

    Workflow contracts:

    "agent_reasoning":
        Input:  {agent_id, agent_name, agent_type, categories,
                 evidence: [{id, category, title, summary, sentiment, strength}],
                 market_price: float, region_id: str, direction: str, trade_size: float}
        Output: {reasoning: str, conviction: str}

    "trade_decision":
        Input:  {agent_id, private_belief: float, market_price: float,
                 effective_confidence: float, current_position: float, max_position: float}
        Output: {direction: "BUY"|"SELL"|null, size: float, rationale: str}

    TODO: Langflow — implement both workflow contracts above.
    """

    def __init__(self):
        self.base_url = config.LANGFLOW_BASE_URL
        self.api_key = config.LANGFLOW_API_KEY
        self._session = None  # TODO: Langflow — initialize httpx.AsyncClient here

    def run_workflow(self, workflow_id: str, inputs: dict) -> dict:
        """
        Execute a Langflow workflow synchronously.

        TODO: Langflow — replace NotImplementedError with:
            import httpx
            response = httpx.post(
                f"{self.base_url}/api/v1/run/{workflow_id}",
                json={"inputs": inputs},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["outputs"][0]["results"]
        """
        raise NotImplementedError(
            f"Langflow workflow '{workflow_id}' was called but LANGFLOW_ENABLED is True "
            f"without an implementation. See app/rag/langflow_client.py."
        )

    async def run_workflow_async(self, workflow_id: str, inputs: dict) -> dict:
        """
        Execute a Langflow workflow asynchronously.

        TODO: Langflow — replace with async httpx call:
            async with httpx.AsyncClient() as client:
                response = await client.post(...)
                return response.json()["outputs"][0]["results"]
        """
        raise NotImplementedError(
            f"Async Langflow workflow '{workflow_id}' not implemented. "
            f"See app/rag/langflow_client.py."
        )

    def health_check(self) -> bool:
        """
        TODO: Langflow — check if Langflow instance is reachable.
        """
        return False


# Singleton — imported by AgentReasoner
langflow_client = LangflowClient()
