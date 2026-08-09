FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY yasinai ./yasinai
COPY security_platform ./security_platform
COPY developer_platform ./developer_platform
COPY knowledge_platform ./knowledge_platform

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir . \
    && useradd --system --uid 10001 --no-create-home yasinai \
    && chown -R yasinai:yasinai /app

COPY . .
RUN chown -R yasinai:yasinai /app

USER 10001:10001

EXPOSE 8000

CMD ["yasin", "status"]
