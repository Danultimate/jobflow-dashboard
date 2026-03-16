# Job Application Dashboard

Personal job application dashboard with:
- Job ingestion and tracking
- AI-assisted cover letter and application review
- LinkedIn source adapter (compliant-first, automation optional)
- VPS-ready deployment with Ollama integration

## Monorepo Layout

- `frontend`: Next.js dashboard UI
- `backend`: FastAPI API, domain logic, workers, and AI orchestration
- `infra`: Docker Compose and Nginx for deployment

## Quick Start

1. Copy environment file templates:
   - `cp backend/.env.example backend/.env`
   - `cp frontend/.env.example frontend/.env.local`
2. Start services from `infra`:
   - `docker compose up --build`
3. Open:
   - Frontend: `http://localhost`
   - API docs: `http://localhost/api/docs`

## Notes

- By default, automation features are disabled (`ENABLE_AUTOMATION=false`).
- The backend expects Ollama at `OLLAMA_BASE_URL`, defaulting to `http://ollama:11434`.
- API authentication is enabled via `/api/auth/login` using `AUTH_USERNAME` and `AUTH_PASSWORD`.
