# Polymolt — Claude Code Instructions

## Project Summary
Polymolt is a real-time prediction market for regional sustainability. AI agents with asymmetric knowledge trade on "Is this region sustainable?" The probability emerges from market dynamics, not a weighted formula.

## Tech Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (in `/frontend`)
- **Backend**: FastAPI (in `/backend`). Calling the route runs the **RAG + specialized system-prompt agent** pipeline.
- **Pipeline**: Implemented in `backend/app/pipeline.py` and `backend/app/rag.py`; flow JSON lives in `backend/langflow_pipeline/` as reference.

## Directory Structure
```
polymolt/
  backend/               # FastAPI app; POST /run runs the pipeline
    app/
      pipeline.py        # RAG + system prompt + LLM
      rag.py             # Embeddings + Chroma retrieval
      config.py
    main.py
    langflow_pipeline/   # Flow JSON (reference)
    langflow_components/ # Custom Langflow components (for Langflow UI)
  frontend/
  docs/
```

## Commands
```bash
# Backend (run the pipeline via POST /run)
cd backend && pip install -r requirements.txt && export OPENAI_API_KEY=... && python -m uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## Key Design
- **POST /run** with body `{ "message": "...", "system_prompt": "..." (optional), "use_rag": true }` runs the pipeline and returns `{ "response": "..." }`.
- Pipeline: optional RAG retrieval (embed query → Chroma) → prompt (system + context + message) → OpenAI → response.
