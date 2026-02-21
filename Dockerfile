# ── Build stage: install dependencies ────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download NLTK corpora used by TextBlob
RUN PYTHONPATH=/install/lib/python3.12/site-packages \
    python -c "import textblob; import subprocess; subprocess.run(['python','-m','textblob.download_corpora'])"

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Non-root user for security
RUN addgroup --system tradex && adduser --system --ingroup tradex tradex

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source
COPY --chown=tradex:tradex . .

# Ensure runtime directories exist and are writable by tradex user
RUN mkdir -p /app/logs /app/data /app/reports \
    && chown -R tradex:tradex /app/logs /app/data /app/reports

USER tradex

CMD ["python", "hardcore_training.py"]
