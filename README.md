# Context Forge

A full-stack Retrieval-Augmented Generation (RAG) system that lets users upload
technical documents (PDF/DOCX) and ask questions answered with citations back
to the source chunks.

## Stack
- **Backend**: FastAPI, LangChain, ChromaDB (vector store), PostgreSQL (users/chat history), JWT auth
- **LLM**: Groq (free tier) running Llama 3.1 8B Instant
- **Frontend**: React + Vite
- **Deployment**: Docker Compose, CI via GitHub Actions

## Getting a free Groq API key
1. Go to https://console.groq.com
2. Sign up (free) and create an API key
3. Put it in `backend/.env` as `GROQ_API_KEY=...`

## Local setup

```bash
# 1. Configure backend env
cp backend/.env.example backend/.env
# edit backend/.env and add your GROQ_API_KEY

# 2. Start everything
docker compose up --build

# App will be available at:
# Frontend: http://localhost:5173
# Backend docs: http://localhost:8000/docs
```

## Running backend locally without Docker (optional, for development)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# You'll need a local Postgres running, or point DATABASE_URL at a hosted one
uvicorn app.main:app --reload
```

## Running frontend locally without Docker

```bash
cd frontend
npm install
npm run dev
```

## API Overview
- `POST /api/auth/signup` — create account
- `POST /api/auth/login` — get JWT token
- `POST /api/documents/upload` — upload PDF/DOCX (auth required)
- `GET /api/documents/` — list your documents
- `POST /api/chat/` — ask a question, get answer + source citations
- `GET /api/chat/history` — past conversation

## Architecture

```
React Chat UI --> FastAPI --> LangChain RAG pipeline --> Groq LLM
                     |                |
                PostgreSQL        ChromaDB
             (users, history)   (embeddings, per-user collections)
```

## Notes for resume / interviews
- Each user's documents are isolated in a separate Chroma collection — a
  simple but real multi-tenancy pattern worth explaining in interviews.
- Citations are returned with every answer (filename + chunk index) so
  answers are traceable back to source material — a key RAG evaluation point.
- JWT auth protects all document/chat endpoints.
- CI pipeline lints, tests, and builds Docker images on every push.

## Next steps to extend this project
- Add streaming responses (Server-Sent Events) for a more polished chat UX
- Swap Chroma for Pinecone/Qdrant to demonstrate managed vector DB experience
- Add automated retrieval quality evals (e.g., RAGAS)
- Deploy to Render/Railway/AWS and add the live link to your resume
