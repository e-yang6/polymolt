# Polymolt — Claude Code Instructions

## Project Summary
Polymolt is a real-time prediction market for regional sustainability. AI agents with asymmetric knowledge trade on "Is this region sustainable?" The probability emerges from market dynamics, not a weighted formula.

## Tech Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (in `/frontend`)
- **Backend**: FastAPI + Python (in `/backend`)
- **Realtime**: WebSockets (FastAPI native)
- **State**: In-memory for MVP, structured for DB migration

## Directory Structure
```
polymolt/
  frontend/          # Next.js app
    src/
      app/           # App router pages
      components/    # UI components
      lib/           # Client utilities, WS hook
      types/         # TypeScript interfaces
  backend/
    app/
      agents/        # Agent definitions and behavior
      market/        # Market maker, probability logic
      data/          # Seeded regions and evidence
      rag/           # RAG/retrieval layer interfaces (future)
      api/           # FastAPI routers
      core/          # Config, state, orchestrator
    main.py
  docs/              # Project specs and task files
```

## Working Rules
- Keep files small and modular — no giant files
- Preserve RAG integration points as TODO stubs
- The market probability must emerge from agent trades, not a direct formula
- Leave `# TODO: RAG` and `# TODO: Langflow` comments at integration points

## Commands
```bash
# Backend (use python -m to ensure correct Python version)
cd backend && python -m pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## Key Design Decisions
- LMSR-inspired market maker for probability updates
- 9 agents with asymmetric knowledge and behavior traits
- 6 sustainability categories with seeded evidence
- WebSocket broadcast after each trade
- Agent knowledge access controls which evidence they can read

## Phase Status
- [ ] Phase 1: Scaffold + MVP
- [ ] Phase 2: Market Realism
- [ ] Phase 3: RAG/Langflow Architecture
- [ ] Phase 4: UI Polish
- [ ] Phase 5: Demo Readiness
