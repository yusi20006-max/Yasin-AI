FROM python:3.12-slim

WORKDIR /app

# Install as non-root-ready layout; secrets must never be baked into the image.
COPY pyproject.toml README.md LICENSE ./
COPY yasinai ./yasinai
COPY security_platform ./security_platform
COPY developer_platform ./developer_platform
COPY knowledge_platform ./knowledge_platform
COPY api_service ./api_service
COPY observability ./observability

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir . \
    && useradd --system --uid 10001 --no-create-home yasinai \
    && chown -R yasinai:yasinai /app

# Remaining repo files (docs, deploy metadata) — no .env / credentials (gitignored)
COPY --chown=yasinai:yasinai . .

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD yasin status || exit 1

CMD ["yasin", "status"]
