"""
WebSocket + REST router for the prediction market simulation.

Endpoints:
    WS  /ws/{region_id}          — streams market simulation
    GET /regions                 — list available regions
    POST /market/{region_id}/shock — inject an external shock
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.market.engine import MarketEngine, REGIONS
from app.market.agents import (
    SimAgent,
    create_default_agents,
    pick_evidence,
    generate_reasoning,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["market"])

# In-memory shock queue per region
_shock_queue: dict[str, list[dict[str, Any]]] = {}


@router.get("/regions")
def list_regions():
    return {"regions": [r.to_dict() for r in REGIONS.values()]}


@router.post("/market/{region_id}/shock")
def shock_market(
    region_id: str,
    shock_type: str = Query(..., description="positive or negative"),
    rounds: int = Query(20, ge=1, le=100),
):
    if region_id not in REGIONS:
        return {"error": f"Unknown region: {region_id}"}

    _shock_queue.setdefault(region_id, []).append({
        "type": shock_type,
        "rounds": rounds,
    })
    return {"status": "queued", "shock_type": shock_type, "rounds": rounds}


# ---------------------------------------------------------------------------
# WebSocket simulation
# ---------------------------------------------------------------------------

def _build_trade_entry(
    agent: SimAgent,
    direction: str,
    size: float,
    price_before: float,
    price_after: float,
    evidence_titles: list[str],
    trade_id: str,
) -> dict[str, Any]:
    return {
        "id": trade_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agentId": agent.id,
        "agentName": agent.name,
        "agentType": agent.agent_type,
        "direction": direction,
        "size": round(size, 3),
        "priceBefore": round(price_before, 6),
        "priceAfter": round(price_after, 6),
        "reasoning": agent.last_reasoning,
        "evidenceTitles": evidence_titles,
    }


async def _send_json(ws: WebSocket, msg: dict[str, Any]) -> bool:
    """Send JSON; return False if the socket is closed."""
    try:
        await ws.send_text(json.dumps(msg))
        return True
    except Exception:
        return False


@router.websocket("/ws/{region_id}")
async def market_ws(ws: WebSocket, region_id: str):
    if region_id not in REGIONS:
        await ws.close(code=4000, reason=f"Unknown region: {region_id}")
        return

    await ws.accept()
    logger.info("WS connected: region=%s", region_id)

    engine = MarketEngine(region=REGIONS[region_id])
    agents = create_default_agents(engine.current_price)

    # Send initial market_reset
    await _send_json(ws, {
        "type": "market_reset",
        "data": {
            **engine.snapshot(),
            "agents": [a.to_dict() for a in agents],
            "recentTrades": [],
        },
    })

    # Listen for client messages in parallel
    async def listen():
        nonlocal engine, agents, region_id
        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                msg_type = msg.get("type", "")

                if msg_type == "pong":
                    pass  # heartbeat ack; ignore

                elif msg_type == "reset":
                    engine.reset()
                    agents = create_default_agents(engine.current_price)
                    await _send_json(ws, {
                        "type": "market_reset",
                        "data": {
                            **engine.snapshot(),
                            "agents": [a.to_dict() for a in agents],
                            "recentTrades": [],
                        },
                    })

                elif msg_type == "change_region":
                    new_id = msg.get("regionId", region_id)
                    if new_id in REGIONS:
                        region_id = new_id
                        engine = MarketEngine(region=REGIONS[region_id])
                        agents = create_default_agents(engine.current_price)
                        await _send_json(ws, {
                            "type": "market_reset",
                            "data": {
                                **engine.snapshot(),
                                "agents": [a.to_dict() for a in agents],
                                "recentTrades": [],
                            },
                        })

        except (WebSocketDisconnect, Exception):
            pass

    listener = asyncio.create_task(listen())

    try:
        round_counter = 0
        while True:
            # Simulation tick
            await asyncio.sleep(1.2)  # ~1.2s per round for a nice cadence

            # Apply queued shocks
            shocks = _shock_queue.pop(region_id, [])
            for shock in shocks:
                shift = 0.08 if shock["type"] == "positive" else -0.08
                for agent in agents:
                    agent.current_belief = max(
                        0.01, min(0.99, agent.current_belief + shift * (1 - agent.stubbornness))
                    )

            # Each agent gets a chance to trade
            import random
            random.shuffle(agents)
            for agent in agents:
                agent.update_belief(engine.current_price)
                decision = agent.decide_trade(engine.current_price)

                if decision is None:
                    continue

                direction, size = decision
                evidence = pick_evidence(2)
                agent.evidence_used = evidence
                agent.last_reasoning = generate_reasoning(agent, direction, evidence)

                price_before, price_after = engine.execute_trade(direction, size)
                trade_id = engine.make_trade_id()

                trade_entry = _build_trade_entry(
                    agent, direction, size,
                    price_before, price_after,
                    [e.title for e in evidence],
                    trade_id,
                )
                agent.record_trade(trade_entry)

                ok = await _send_json(ws, {
                    "type": "trade",
                    "data": {
                        "trade": trade_entry,
                        "agent": agent.to_dict(),
                        "market": engine.snapshot(),
                    },
                })
                if not ok:
                    return

            # Ping every 10 rounds
            round_counter += 1
            if round_counter % 10 == 0:
                await _send_json(ws, {"type": "ping"})

    except (WebSocketDisconnect, Exception) as e:
        logger.info("WS disconnected: %s", e)
    finally:
        listener.cancel()
