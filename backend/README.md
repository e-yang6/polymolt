# PolyMolt Backend

FastAPI app that runs the **RAG + specialized system-prompt agent** pipeline when you call the route.

## Run the backend

```bash
cd backend
python -m pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
python -m uvicorn main:app --reload --port 8000
```

## Trigger the pipeline

**POST /run** — the pipeline runs on every call.

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main climate risks for Scandinavia?"}'
```

Optional body fields:

- **message** (required): User question or message.
- **system_prompt** (optional): Override the default agent system prompt (e.g. "You are a policy expert. Answer only from the context.").
- **use_rag** (optional, default `true`): If `true`, the query is embedded and the vector store is searched for context; if `false`, only system prompt + message are sent to the LLM.

Response:

```json
{ "response": "..." }
```

## Environment

- **OPENAI_API_KEY** (required for pipeline): Used for embeddings (RAG) and chat (LLM).
- **EMBED_MODEL** (optional): Default `text-embedding-3-small`.
- **CHAT_MODEL** (optional): Default `gpt-4o-mini`.

## RAG

- The app uses **ChromaDB** in-memory for the vector store. If no documents have been added, RAG returns no context and the prompt still runs with "(No RAG context loaded.)".
- To add documents, use the `app.rag` module (e.g. from a script or an admin route): `add_documents(texts, ids)`.

## Layout

- **main.py** — FastAPI app; **POST /run** calls `run_pipeline()`.
- **app/pipeline.py** — Builds prompt (system + RAG context + message), calls OpenAI, returns response.
- **app/rag.py** — Embeddings + Chroma retrieval.
- **app/config.py** — Env config.
- **langflow_pipeline/** — Reference flow JSON (same logic as the code).
