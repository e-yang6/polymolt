# Polymolt

> Real-time prediction market for regional sustainability — powered by AI agents with asymmetric knowledge.

## What Is This?

Polymolt is a Polymarket-style prediction market where **9 AI agents** trade on whether a selected region is sustainable. Each agent has different knowledge access, confidence levels, risk tolerance, and behavioral traits. The sustainability signal **emerges from market interaction** — not a formula.

It's also a study in LLM-like behavior under asymmetric information: how do agents with different evidence sets converge or disagree? When does a stubborn specialist override a cautious generalist?

## Features

- **Live market probability chart** — updates after every trade, tooltip shows agent name + direction
- **Real-time trade feed** — agent name, direction, size, before/after probability, explanation
- **9 agent cards** — specialists, hybrids, master generalist; flash on belief update, show last trade delta
- **Agent detail panel** — categories, evidence, reasoning, behavior traits, belief history sparkline
- **Behavior study view** — toggle panel ranking all 9 agents' beliefs vs. market price
- **3 seeded demo regions** — Scandinavia (sustainable), Sub-Saharan Drought Belt (weak), Industrial Delta (contested)
- **Shock events** — inject crisis or recovery scenarios mid-simulation; agents react within 2–3 rounds
- **WebSocket-driven** — everything updates live in the browser

## Architecture

```
Browser ←→ Next.js Frontend
              ↕ WebSocket / REST
           FastAPI Backend
              ├── Agent Engine (9 agents, asymmetric knowledge)
              ├── Market Maker (LMSR-inspired)
              ├── Evidence Store (seeded, RAG-ready)
              └── Orchestrator (trade loop, broadcast)
```

## Quick Start

**Prerequisites**: Python 3.11+, Node 18+

```bash
# 1. Clone and enter
cd polymolt

# 2. Backend
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Open http://localhost:3000
```

## Sustainability Categories

1. Climate & Emissions
2. Energy & Resource Systems
3. Water & Ecosystems
4. Infrastructure & Built Environment
5. Economy & Social Resilience
6. Governance & Policy

## Agent Roster

| Agent | Type | Power | Categories |
|-------|------|-------|------------|
| Climate Agent | Specialist | 1.0x | Climate & Emissions |
| Energy Agent | Specialist | 1.0x | Energy & Resource Systems |
| Water & Ecosystem Agent | Specialist | 1.0x | Water & Ecosystems |
| Infrastructure Agent | Specialist | 1.0x | Infrastructure & Built Environment |
| Social Resilience Agent | Specialist | 1.0x | Economy & Social Resilience |
| Governance Agent | Specialist | 1.0x | Governance & Policy |
| Environmental Generalist | Hybrid | 1.5x | Climate, Energy, Water |
| Human Systems Generalist | Hybrid | 1.5x | Infrastructure, Social, Governance |
| Master Generalist | Master | 2.0x | All 6 categories |

## Demo API

```bash
# Inject a crisis event (agents react in ~2–3 rounds)
curl -X POST http://localhost:8000/market/scandinavia/shock?shock_type=negative

# Inject a recovery event
curl -X POST http://localhost:8000/market/scandinavia/shock?shock_type=positive

# Reset a specific region
curl -X POST http://localhost:8000/market/scandinavia/reset
```

Or use the **Shock** / **Recover** buttons in the UI.

## Future: RAG + Langflow

The architecture preserves clean integration points for:
- Category-based vector corpora (one per sustainability category)
- Agent-specific retrieval access controls
- Langflow orchestration workflows

See `docs/04_rag_langflow_design.md` for the full design.

## Docs

- [Project Overview](docs/00_project_overview.md)
- [Product Requirements](docs/01_product_requirements.md)
- [Agent Design](docs/02_agent_design.md)
- [Market Logic](docs/03_market_logic.md)
- [RAG/Langflow Design](docs/04_rag_langflow_design.md)
- [Frontend Spec](docs/05_frontend_spec.md)
- [Build Phases](docs/06_build_phases.md)
