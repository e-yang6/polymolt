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
from app.agents.reasoning import template_reason
from app.market.lmsr import apply_trade
from fastapi import WebSocket

logger = logging.getLogger(__name__)

# Delay between individual agent trades (seconds)
TRADE_INTERVAL = 1.2

# Delay between full rounds (seconds)
ROUND_INTERVAL = 2.0


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
    market_price = state.market.current_price
    region_id = state.market.region_id

    # Form new belief
    new_belief, evidence_used = form_belief(
        agent=agent_state.config,
        region_id=region_id,
        prior_belief=agent_state.current_belief,
        market_price=market_price,
    )
    agent_state.current_belief = new_belief
    agent_state.evidence_used = evidence_used

    # Decide whether to trade
    direction, size = compute_trade(
        agent=agent_state.config,
        private_belief=new_belief,
        market_price=market_price,
        evidence_used=evidence_used,
    )

    if direction is None:
        # Agent skips this round — still broadcast belief update
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

    # Generate reasoning
    reasoning = template_reason(
        agent=agent_state.config,
        evidence_used=evidence_used,
        private_belief=new_belief,
        market_price=price_before,
        direction=direction,
        trade_size=size,
    )
    agent_state.last_reasoning = reasoning

    # Record trade
    trade = state.record_trade(
        agent_state=agent_state,
        direction=direction,
        size=size,
        price_before=price_before,
        price_after=price_after,
        reasoning=reasoning,
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
