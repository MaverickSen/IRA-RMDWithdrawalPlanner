# ---------- Base Stage: Install dependencies ----------
FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .


# ---------- Final Runtime Stage ----------
FROM python:3.12-slim

WORKDIR /app

# Install only runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from base (without re-running tests)
COPY --from=base /app /app

# Environment variable placeholder (value injected at runtime)
ENV OPENAI_API_KEY=""

# Default command: run the CLI
CMD ["python", "main.py"]