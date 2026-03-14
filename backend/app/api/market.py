"""REST endpoints for market state and control."""

import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.core.state import app_state
from app.core.orchestrator import run_simulation, stop_simulation
from app.data.regions import get_region

router = APIRouter(prefix="/market", tags=["market"])

# Track running simulation task
_simulation_task: asyncio.Task | None = None


@router.get("/{region_id}")
def get_market_state(region_id: str):
    if app_state.market is None or app_state.market.region_id != region_id:
        raise HTTPException(status_code=404, detail="No active market for this region")
    return {
        "market": app_state.market.to_dict(),
        "agents": [a.to_dict() for a in app_state.agents.values()],
        "recentTrades": [t.to_dict() for t in app_state.market.trade_log[-20:]],
    }


@router.post("/{region_id}/start")
async def start_market(region_id: str, background_tasks: BackgroundTasks):
    global _simulation_task

    region = get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    # Stop any existing simulation
    if _simulation_task and not _simulation_task.done():
        stop_simulation(app_state)
        await asyncio.sleep(0.5)

    # Reset state for new region
    app_state.reset_for_region(region_id, b=region["lmsr_b"])

    # Start simulation as background task
    _simulation_task = asyncio.create_task(run_simulation(app_state))

    return {"status": "started", "region_id": region_id}


@router.post("/{region_id}/reset")
async def reset_market(region_id: str):
    global _simulation_task

    region = get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    # Stop current simulation
    if _simulation_task and not _simulation_task.done():
        stop_simulation(app_state)
        await asyncio.sleep(0.3)

    # Reset
    app_state.reset_for_region(region_id, b=region["lmsr_b"])

    # Restart
    _simulation_task = asyncio.create_task(run_simulation(app_state))

    return {"status": "reset", "region_id": region_id}


@router.post("/{region_id}/stop")
def stop_market(region_id: str):
    stop_simulation(app_state)
    return {"status": "stopped"}
