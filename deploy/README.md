# Deployment

## Production baseline

1. Copy `.env.example` to `.env` and provide only non-secret runtime configuration there.
2. Build and start with `docker compose -f compose.production.yml up -d --build`.
3. Inspect service state with `docker compose -f compose.production.yml ps`.
4. Inspect logs with `docker compose -f compose.production.yml logs --tail=200`.

The production profile uses a persistent named volume, a read-only root filesystem, dropped Linux capabilities, `no-new-privileges`, bounded CPU/memory/PID resources, and a container healthcheck.
