# SBI Mutual Fund FAQ Assistant

A facts-only, Retrieval-Augmented Generation (RAG) chatbot for selected SBI Mutual Fund schemes. The assistant answers factual questions using only official mutual fund documentation and strictly refuses to provide investment advice, recommendations, or buy/sell suggestions.

---

## Supported Schemes & Fields

### Schemes
1. **SBI Flexicap Fund**
2. **SBI ELSS Tax Saver Fund**
3. **SBI Large Cap Fund**

### Question Categories
* Total Expense Ratio (TER) / expense ratio
* Exit load
* Minimum investment / application amount
* Minimum SIP amount
* Benchmark index
* Risk level / riskometer
* Lock-in period
* Investment objective

---

## Tech Stack
* **Language**: Python 3.9+
* **Backend Framework**: FastAPI (Uvicorn ASGI server)
* **Frontend Interface**: Streamlit
* **RAG Framework**: LangChain
* **Vector Store**: FAISS
* **PDF & Data Parsing**: PyPDF & OpenPyXL
* **Model Configuration**: Groq `llama3-70b-8192` by default, with optional OpenAI `gpt-4o-mini` support (and local developer mock fallback mode)

---

## Submission Deliverables

The following submission-ready documents are located in the project root:
1. **[source-list.md](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/source-list.md)**: Official source registry including filenames and SHA256 checksums.
2. **[sample-qa.md](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/sample-qa.md)**: Representative Q&A examples for factual, refusal, ambiguous, and missing information queries.
3. **[disclaimer.md](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/disclaimer.md)**: The chatbot's facts-only scope and advice refusal statement.
4. **[demo-instructions.md](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/demo-instructions.md)**: Clear commands to run the backend, frontend, and tests locally.

---

## Project Structure

```text
├── README.md                      # Project documentation
├── source-list.md                 # Approved source files registry
├── sample-qa.md                   # Sample QA test queries and answers
├── disclaimer.md                  # Chatbot policy and disclaimer snippet
├── demo-instructions.md           # Instructions to run the application
├── requirements.txt               # Main python dependencies
├── pyproject.toml                 # Package details and test configuration
├── data/
│   ├── source_docs/               # Raw official factsheets and TER data files
│   ├── source_registry.json       # Document registration registry
│   └── vector_store/              # FAISS index records and embeddings
├── src/
│   └── sbi_fund_faq/
│       ├── api/                   # FastAPI backend endpoints and Streamlit frontend
│       ├── chatbot/               # LLM generation, guardrails, and citation validation
│       ├── config/                # Environment variables settings configuration
│       ├── ingestion/             # PDF and Excel document parser pipeline
│       └── retrieval/             # Normalization, chunking, and vector retriever
└── tests/                         # Unit and integration test suites
```
