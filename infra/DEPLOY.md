# VPS Deployment Guide

## 1) Prepare environment files

From repository root:

- `cp backend/.env.example backend/.env`
- `cp frontend/.env.example frontend/.env.local`
- `cp infra/.env.example infra/.env`

Update these values:
- `backend/.env`: set `DATABASE_URL`, `REDIS_URL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- `frontend/.env.local`: set `NEXT_PUBLIC_API_BASE_URL` to your public domain path, for example `https://your-domain.com/api`

If Ollama already runs as an external container on the same VPS:
- Set `OLLAMA_BASE_URL=http://<ollama-host>:11434`

## 2) Start stack

From `infra` directory:

- `docker compose --env-file .env up -d --build`

## 3) Verify health

- `docker compose ps`
- `curl http://localhost/health`
- Open `http://<server-ip-or-domain>`

## 4) Migrations

The app creates tables on startup. Optional explicit migration command:

- `docker compose exec backend alembic upgrade head`

## 5) Hardening recommendations

- Put Nginx behind Cloudflare or a firewall.
- Add HTTPS termination (Caddy/Traefik or certbot).
- Restrict API with auth (JWT/session) before internet exposure.
- Set DB backups (nightly dump + offsite storage).
