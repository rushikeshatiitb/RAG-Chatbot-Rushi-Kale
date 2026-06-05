# Local Demo & Execution Instructions

Follow these instructions to run the **SBI Mutual Fund FAQ Assistant** locally for evaluation.

---

## 1. Environment Configuration

The application requires a `.env` file at the root. You can bootstrap this from [.env.example](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/.env.example):

```bash
cp .env.example .env
```

If you wish to test with live Groq calls, add your API key:
```text
GROQ_API_KEY="your-real-groq-api-key"
```
Or, if you want to use the optional OpenAI backend:
```text
MODEL_PROVIDER=openai
CHAT_MODEL=gpt-4o-mini
OPENAI_API_KEY="your-real-openai-api-key"
```
*Note: If no API key is specified, the application automatically runs in a **mock developer mode**, allowing you to query all schemes/fields and receive simulated factual responses without generating API expenses.*

---

## 2. Rebuilding the Vector Store Index (Optional)
If you want to re-ingest and re-index the official PDF factsheets and Excel TER reports:
```bash
.venv/bin/python -m sbi_fund_faq.retrieval.index
```

---

## 3. Running the Streamlit Interface

The Streamlit UI has a **standalone fallback mode** which operates without needing a running backend server.

1. **Launch the interface:**
   ```bash
   .venv/bin/streamlit run src/sbi_fund_faq/api/ui.py
   ```
2. **Access in browser:**
   Open [http://localhost:8501](http://localhost:8501).

---

## 4. Running the React Frontend (Premium Dashboard)

The React frontend offers a high-fidelity, wealth-tech style UI with glassmorphic visuals, query-template chips, and live reference panels showing grounding scores.

1. **Launch the development server:**
   ```bash
   cd frontend
   npm run dev
   ```
2. **Access in browser:**
   Open [http://localhost:5173](http://localhost:5173).
3. **Standalone mode:**
   If the FastAPI server is not running, the React app automatically falls back to client-side simulated responses.

---

## 5. Running the FastAPI Backend (Optional)

If you wish to run the app as a separate API server:

1. **Start the FastAPI server:**
   ```bash
   .venv/bin/uvicorn sbi_fund_faq.__main__:app --reload --port 8000
   ```
2. **Verify server is running:**
   Access the health endpoint: `curl http://127.0.0.1:8000/health`
3. **Query via HTTP POST:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the exit load of SBI Flexicap Fund?"}'
   ```

---

## 6. Running the Test Suite
To execute the automated unit, integration, and evaluation test suites (77 tests total):
```bash
.venv/bin/pytest
```
