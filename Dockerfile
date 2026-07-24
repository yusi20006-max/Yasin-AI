FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false

COPY . .
RUN poetry install --no-root && pip install .

EXPOSE 8000

CMD ["yasin", "status"]
