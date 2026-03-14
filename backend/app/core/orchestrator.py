"""
Simulation orchestrator — runs the agent trading loop.
Shuffles agents each round, triggers belief updates and trades,
applies LMSR updates, and broadcasts via WebSocket.
"""

import asyncio
import json
import random
import logging
from app.core.state import AppState, AgentState
from app.agents.belief_engine import form_belief
from app.agents.trade_engine import compute_trade
from app.rag.reasoning import agent_reasoner      # Phase 3: routes template or Langflow
from app.market.lmsr import apply_trade
from fastapi import WebSocket

from app.core.config import config

logger = logging.getLogger(__name__)

# Configurable via TRADE_INTERVAL and ROUND_INTERVAL env vars (see core/config.py)
TRADE_INTERVAL = config.TRADE_INTERVAL_SECONDS
ROUND_INTERVAL = config.ROUND_INTERVAL_SECONDS


async def broadcast(state: AppState, message: dict):
    """Send a JSON message to all connected WebSocket clients."""
    if not state.connections:
        return
    data = json.dumps(message)
    dead = set()
    for ws in list(state.connections):
        try:
            await ws.send_text(data)
        except Exception:
            dead.add(ws)
    for ws in dead:
        state.connections.discard(ws)


async def run_simulation(state: AppState):
    """
    Main simulation loop. Runs indefinitely until market.is_running = False.
    Each round: shuffle agents → for each agent → form belief → trade → broadcast.
    """
    if state.market is None:
        logger.warning("Simulation started with no market state.")
        return

    state.market.is_running = True
    logger.info(f"Starting simulation for region: {state.market.region_id}")

    # Broadcast initial market state
    await broadcast(state, {
        "type": "market_reset",
        "data": {
            **state.market.to_dict(),
            "agents": [a.to_dict() for a in state.agents.values()],
        }
    })

    await asyncio.sleep(1.0)

    while state.market.is_running:
        agent_list = list(state.agents.values())
        random.shuffle(agent_list)

        for agent_state in agent_list:
            if not state.market.is_running:
                break

            await _process_agent_turn(state, agent_state)
            await asyncio.sleep(TRADE_INTERVAL)

        await asyncio.sleep(ROUND_INTERVAL)

    logger.info(f"Simulation stopped for region: {state.market.region_id}")


async def _process_agent_turn(state: AppState, agent_state: AgentState):
    """Run one agent's belief update and potential trade."""
    try:
        await _process_agent_turn_inner(state, agent_state)
    except Exception as e:
        logger.warning(f"Agent turn error ({agent_state.config.id}): {e}")


async def _process_agent_turn_inner(state: AppState, agent_state: AgentState):
    """Inner logic — separated so outer wrapper can catch and skip on error."""
    market_price = state.market.current_price
    momentum = state.market.price_momentum
    region_id = state.market.region_id

    # Form new belief — now with momentum signal
    new_belief, evidence_used = form_belief(
        agent=agent_state.config,
        region_id=region_id,
        prior_belief=agent_state.current_belief,
        market_price=market_price,
        momentum=momentum,
    )
    agent_state.current_belief = new_belief
    agent_state.evidence_used = evidence_used

    # Decide whether to trade — now with effective_confidence and position
    direction, size = compute_trade(
        agent=agent_state.config,
        private_belief=new_belief,
        market_price=market_price,
        evidence_used=evidence_used,
        effective_confidence=agent_state.effective_confidence,
        current_position=agent_state.current_position,
    )

    if direction is None:
        # Agent skips this round — apply confidence decay, broadcast belief update
        agent_state.apply_confidence_decay()
        await broadcast(state, {
            "type": "agent_update",
            "data": agent_state.to_dict(),
        })
        return

    # Apply LMSR trade
    new_q_yes, new_q_no, price_before, price_after = apply_trade(
        q_yes=state.market.q_yes,
        q_no=state.market.q_no,
        b=state.market.b,
        direction=direction,
        size=size,
    )
    state.market.q_yes = new_q_yes
    state.market.q_no = new_q_no

    # Generate reasoning — routes through AgentReasoner (template or Langflow)
    reason_result = agent_reasoner.reason(
        agent=agent_state.config,
        evidence=evidence_used,
        market_price=price_before,
        region_id=region_id,
        private_belief=new_belief,
        direction=direction,
        trade_size=size,
    )
    agent_state.last_reasoning = reason_result.reasoning

    # Record trade (also calls refresh_confidence internally)
    trade = state.record_trade(
        agent_state=agent_state,
        direction=direction,
        size=size,
        price_before=price_before,
        price_after=price_after,
        reasoning=reason_result.reasoning,
        evidence_used=evidence_used,
    )

    # Broadcast trade + updated agent + market
    await broadcast(state, {
        "type": "trade",
        "data": {
            "trade": trade.to_dict(),
            "agent": agent_state.to_dict(),
            "market": state.market.to_dict(),
        }
    })


def stop_simulation(state: AppState):
    """Signal the simulation loop to stop."""
    if state.market:
        state.market.is_running = False
