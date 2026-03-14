"""WebSocket endpoint for real-time market updates."""

import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.state import app_state
from app.core.orchestrator import run_simulation, stop_simulation

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

_simulation_task: asyncio.Task | None = None


@router.websocket("/ws/{region_id}")
async def websocket_endpoint(websocket: WebSocket, region_id: str):
    global _simulation_task

    await websocket.accept()
    app_state.add_connection(websocket)
    logger.info(f"WebSocket connected: region={region_id}")

    try:
        # If no market or different region, start fresh
        if app_state.market is None or app_state.market.region_id != region_id:
            from app.data.regions import get_region
            region = get_region(region_id)
            if not region:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": f"Unknown region: {region_id}"}
                }))
                return

            # Stop existing simulation if running
            if _simulation_task and not _simulation_task.done():
                stop_simulation(app_state)
                await asyncio.sleep(0.3)

            app_state.reset_for_region(region_id, b=region["lmsr_b"])
            _simulation_task = asyncio.create_task(run_simulation(app_state))
        elif not app_state.market.is_running:
            # Market exists but stopped — restart it
            from app.data.regions import get_region
            region = get_region(region_id)
            app_state.reset_for_region(region_id, b=region["lmsr_b"])
            _simulation_task = asyncio.create_task(run_simulation(app_state))
        else:
            # Market already running — send current state to new connection
            await websocket.send_text(json.dumps({
                "type": "market_reset",
                "data": {
                    **app_state.market.to_dict(),
                    "agents": [a.to_dict() for a in app_state.agents.values()],
                    "recentTrades": [t.to_dict() for t in app_state.market.trade_log[-20:]],
                }
            }))

        # Keep connection alive, handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                msg = json.loads(data)

                if msg.get("type") == "change_region":
                    new_region_id = msg.get("regionId")
                    from app.data.regions import get_region
                    region = get_region(new_region_id)
                    if region:
                        if _simulation_task and not _simulation_task.done():
                            stop_simulation(app_state)
                            await asyncio.sleep(0.3)
                        app_state.reset_for_region(new_region_id, b=region["lmsr_b"])
                        _simulation_task = asyncio.create_task(run_simulation(app_state))

                elif msg.get("type") == "reset":
                    from app.data.regions import get_region
                    current_region = app_state.market.region_id if app_state.market else region_id
                    region = get_region(current_region)
                    if _simulation_task and not _simulation_task.done():
                        stop_simulation(app_state)
                        await asyncio.sleep(0.3)
                    app_state.reset_for_region(current_region, b=region["lmsr_b"])
                    _simulation_task = asyncio.create_task(run_simulation(app_state))

                elif msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

            except asyncio.TimeoutError:
                # Send keepalive ping
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: region={region_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        app_state.remove_connection(websocket)
