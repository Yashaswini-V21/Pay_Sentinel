# Deployment Guide — Pay_Sentinel

This document describes simple, production-ready steps to host Pay_Sentinel using Docker.

Prerequisites
- Docker & Docker Compose installed
- A container registry (Docker Hub, GitHub Container Registry, GCR, etc.)
- `models/` directory populated with trained model files or volume-mounted storage

1) Build the production image

```bash
docker build -t <your-registry>/paysentinel:latest --target production .
```

2) Push the image to your registry

```bash
docker push <your-registry>/paysentinel:latest
```

3) Run with the provided production compose

- Copy the example env file and edit secrets:

```bash
cp .env.production.example .env.production
# Edit .env.production: set PAYSENTINEL_API_KEY and ANTHROPIC_API_KEY if used
```

- Start services (build will use local image if present):

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

4) Verify

```bash
docker ps
curl http://localhost/api/health
```

5) Notes & recommendations
- Use a secrets manager or CI to inject secret env vars; do not commit `.env.production`.
- Ensure the `models/` directory on the host contains the model files listed in `models/`.
- Configure a reverse proxy (the repo includes `nginx/nginx.conf`) and map port 80 to the nginx container.
- Add a small CI job to run `python -m pytest` and `docker build` on push to main before deployment.

If you want, I can:
- Add a GitHub Actions workflow to run tests and build/push the image.
- Create a `docker-compose.override.yml` for local development.
