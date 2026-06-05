FROM python:3.11-slim

# Install system dependencies required by FAISS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement files and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and dataset documents
COPY src/ ./src/
COPY data/ ./data/

# Set Python path to find the packages in src
ENV PYTHONPATH=/app/src

# Run the ingestion and retrieval indexing to build the vector store at build time
RUN python -m sbi_fund_faq.retrieval.index

# Expose default port
EXPOSE 8000

# Start command resolving dynamic $PORT set by Railway
CMD ["sh", "-c", "uvicorn sbi_fund_faq.__main__:app --host 0.0.0.0 --port ${PORT:-8000}"]
