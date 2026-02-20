# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends 
    build-essential 
    libxml2-dev 
    libxslt-dev 
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data for TextBlob (SentimentBot)
RUN python -m textblob.download_corpora

# Copy project files
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Command to run the project status report on startup
CMD ["python", "status_report.py"]
