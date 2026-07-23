# RAG + MCP Agent System

A document Q&A system that routes questions between two agents based on confidence:
- **Sub-agent**: answers grounded in a locally embedded document (RAG via Supabase + pgvector)
- **Tool agent**: falls back to real GitHub tool access via MCP when document search confidence is low

## Stack
Python · FastAPI · LangGraph · Supabase (pgvector) · Gemini API · sentence-transformers (local embeddings) · MCP (GitHub server)

## How it works
1. PDF → extracted, chunked, embedded locally, stored in Supabase (`ingest.py`)
2. User question → embedded → vector search finds top matching chunks (`agents/router.py`)
3. If confidence is high → grounded answer from document (`agents/sub_agent.py`)
4. If confidence is low → hands off to a GitHub-tool-enabled agent via MCP (`agents/tool_agent.py`)
5. LangGraph (`agents/graph.py`) wires it together with conditional routing
6. FastAPI (`main.py`) serves the API + a chat UI

## Run locally
```bash
source venv/bin/activate
uvicorn main:app --reload
```
Visit `http://localhost:8000`

## Environment variables (`.env`)
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
GEMINI_API_KEY=
GITHUB_PAT=
```
