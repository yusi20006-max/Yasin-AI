# Use an official lightweight Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variable defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    YASINAI_ENV=production \
    YASINAI_DOCKER=true

# Copy setup configuration and dependencies first for caching layers
COPY setup.py /app/
COPY requirements.txt* /app/

# Install dependencies if present, and install the package itself
RUN pip install --no-cache-dir .

# Copy the application source code
COPY yasinai/ /app/yasinai/

# Expose port (default 8000)
EXPOSE 8000

# Define final entrypoint
ENTRYPOINT ["yasin"]
CMD ["status"]
