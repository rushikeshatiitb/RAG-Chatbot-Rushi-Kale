# Deployment and Monitoring Guide

This guide details the procedures for deployment, startup checks, structured logging, and document reindexing for the **SBI Mutual Fund FAQ Assistant**.

---

## 1. Deployment Overview

The application consists of two main services:
1. **FastAPI Backend**: Serves query and health endpoints.
2. **Streamlit Frontend**: Provides a user interface.

### Running in Production

To run the application in a production environment:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Backend:**
   Use a production WSGI/ASGI server (like `uvicorn` or `gunicorn` with uvicorn workers):
   ```bash
   uvicorn sbi_fund_faq.__main__:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Start the Streamlit Web UI:**
   ```bash
   streamlit run src/sbi_fund_faq/api/ui.py --server.port 8501 --server.address 0.0.0.0
   ```

---

## 2. Startup Verification Checks

On startup, the FastAPI application performs strict validation checks (configured in `create_app()` inside `src/sbi_fund_faq/api/main.py`). The application refuses to start (raises a `RuntimeError`) if:
* **Approved Sources Validation**: Any registered document in `data/source_registry.json` is missing from `data/source_docs/` or if its SHA256 checksum does not match the registered hash.
* **Vector Index Validation**: The local vector database index files (`records.json` and `embeddings.npy`) are missing, corrupt, or do not match the expected record counts.

---

## 3. Structured Logging & Monitoring

The application uses Python's standard `logging` module configured with a structured console format:
`%(asctime)s [%(levelname)s] %(name)s: %(message)s`

### Key Logged Events:
* **Startup Validation Status**: Logs success or critical validation failure.
* **Incoming Queries**: Logs the raw user question at `INFO` level.
* **Retriever Performance & Classification**: Logs details of retrieval execution time, classifier decisions (advice/factual), and matched chunk count.
* **Grounding Validation Warnings**: Logs a warning if a generated answer fails the citation or grounding checks.

Logs are piped directly to `stdout`/`stderr` to make them compatible with standard container orchestrator log aggregators (e.g. AWS CloudWatch, ELK, Datadog).

---

## 4. Source Updates & Reindexing Process

To update source documents (such as adding a new factsheet or modifying the TER file) and update the vector index:

1. **Place the new/updated file** in the source directory:
   `data/source_docs/`

2. **Calculate the new file's SHA256 checksum:**
   On macOS:
   ```bash
   shasum -a 256 data/source_docs/your-new-file.pdf
   ```

3. **Update the Source Registry:**
   Edit `data/source_registry.json` and update the registry entry with the file's metadata and the calculated `sha256` checksum.

4. **Rebuild the Vector Store:**
   Run the index build script to parse documents, chunk text, generate new embeddings, and rebuild the vector store:
   ```bash
   python -m sbi_fund_faq.retrieval.index
   ```
   *Note: This will recreate the vector store files and the application will start correctly using the updated index on next launch.*
