# Phase-Wise Implementation Plan

## Objective

Build a facts-only Retrieval-Augmented Generation (RAG) chatbot for SBI Mutual Fund that answers factual FAQ-style questions using only approved official SBI Mutual Fund documents and refuses investment advice.

## Phase 1: Project Setup

### Goals

Create the basic project structure, configuration, and development environment needed to build the chatbot.

### Tasks

- Set up application folders for source documents, ingestion, retrieval, chatbot logic, prompts, tests, and documentation.
- Define environment variables for model provider, embedding model, vector store path, and runtime configuration.
- Add dependency management for PDF/document parsing, embeddings, vector storage, and API/UI serving.
- Create a basic application entry point.

### Deliverables

- Project folder structure.
- Dependency file.
- Environment configuration template.
- Basic runnable application skeleton.

### Acceptance Criteria

- The project can be installed and started locally.
- Configuration values are loaded from environment variables.
- No source document data is hardcoded into the chatbot logic.

## Phase 2: Source Document Collection

### Goals

Add the approved official SBI Mutual Fund source documents to the project.

### Tasks

- Collect the following official source documents:
  - SBI Flexicap Fund Factsheet, April 2026
  - SBI ELSS Tax Saver Fund Factsheet, April 2026
  - SBI Large Cap Fund Factsheet, April 2026
  - SBI Total Expense Ratio (TER) Data File
- Store the files in a dedicated source document directory.
- Record source metadata for each document.
- Verify that only approved documents are used for ingestion.

### Deliverables

- Official source documents saved in the project.
- Source metadata registry.
- Approved source allowlist.

### Acceptance Criteria

- The ingestion pipeline can only read documents from the approved source list.
- Each document has a source name, document type, document month, and scheme mapping where applicable.

## Phase 3: Document Parsing and Ingestion

### Goals

Extract text and structured facts from official source documents.

### Tasks

- Implement parsing for factsheet documents.
- Implement parsing for the TER data file.
- Extract page-level or section-level text.
- Preserve citation metadata during extraction.
- Normalize scheme names across all sources.
- Store extracted chunks in an intermediate ingestion output.

### Deliverables

- Document parser.
- TER parser.
- Normalized extracted text and metadata.
- Ingestion output file or database table.

### Acceptance Criteria

- Extracted chunks include `source_name`, `scheme_name`, `document_type`, `document_month`, `page_number`, `section`, and `chunk_text`.
- Text extraction preserves key fields such as expense ratio, exit load, minimum SIP amount, minimum investment amount, benchmark index, riskometer, lock-in period, and investment objective.
- TER values are mapped clearly to the correct scheme and plan.

## Phase 4: Chunking and Metadata Design

### Goals

Prepare source content for accurate retrieval.

### Tasks

- Implement section-aware chunking where possible.
- Keep related facts together in the same chunk.
- Avoid chunks that mix unrelated schemes.
- Attach complete citation metadata to every chunk.
- Generate stable chunk IDs.

### Deliverables

- Chunking module.
- Chunk metadata schema.
- Chunk validation checks.

### Acceptance Criteria

- Every chunk belongs to an approved source document.
- Every chunk has enough metadata to generate a citation.
- Scheme-specific chunks do not combine multiple unrelated schemes.
- Important facts remain retrievable as complete facts.

## Phase 5: Embeddings and Vector Store

### Goals

Index approved source chunks for semantic retrieval.

### Tasks

- Select and configure an embedding model.
- Generate embeddings for all approved chunks.
- Store embeddings and metadata in a vector store.
- Add a rebuild command for refreshing the index.
- Ensure the vector store contains only approved source chunks.

### Deliverables

- Embedding pipeline.
- Vector store.
- Index rebuild command.
- Vector store metadata validation.

### Acceptance Criteria

- User questions can retrieve relevant chunks by scheme and field.
- Vector store records include all required metadata.
- The index can be rebuilt from source documents without manual edits.

## Phase 6: Question Classification and Guardrails

### Goals

Detect advice-seeking questions and refuse them before answer generation.

### Tasks

- Implement a question classifier for factual vs advice-seeking questions.
- Add rules for recommendation, comparison, buy/sell, and personalized advice requests.
- Define a standard refusal response.
- Test refusal behavior with known advice-style prompts.

### Deliverables

- Question classifier.
- Refusal response template.
- Advice question test cases.

### Acceptance Criteria

- Questions such as "Should I invest?", "Which fund is better?", and "Should I buy or sell?" are refused.
- Refused questions do not trigger answer generation from retrieved facts.
- Factual comparison of supported fields can be allowed only when it does not ask for a recommendation.

## Phase 7: Query Normalization

### Goals

Improve retrieval accuracy by mapping user language to known fund fields.

### Tasks

- Normalize scheme names and common aliases.
- Map field aliases to canonical fields.
- Preserve original question intent.
- Add normalization for supported fields:
  - `expense ratio` to `TER`
  - `risk level` to `riskometer`
  - `minimum investment` to `minimum application amount`
  - `SIP minimum` to `minimum SIP amount`

### Deliverables

- Query normalization module.
- Field alias map.
- Scheme alias map.

### Acceptance Criteria

- Common user wording retrieves the correct source chunks.
- Ambiguous scheme names are handled safely.
- Unsupported fields are not invented.

## Phase 8: Retrieval Pipeline

### Goals

Retrieve the most relevant official source chunks for factual user questions.

### Tasks

- Implement top-k vector retrieval.
- Add filters for scheme name and document type where possible.
- Prioritize matching scheme and field.
- Return retrieved chunks with citation metadata.
- Add fallback behavior when no reliable chunk is found.

### Deliverables

- Retriever module.
- Retrieval scoring or filtering logic.
- Retrieval fallback behavior.

### Acceptance Criteria

- Relevant chunks are returned for supported factual questions.
- Expense ratio questions retrieve TER data when appropriate.
- If no reliable source is found, the system returns a "not found in available official sources" response.

## Phase 9: Answer Generation

### Goals

Generate short, factual answers using only retrieved source chunks.

### Tasks

- Create the system prompt for the facts-only assistant.
- Pass retrieved chunks as context to the answer generator.
- Require concise answers.
- Require source citation in every factual answer.
- Prevent model-memory answers.
- Add fallback instructions for missing information.

### Deliverables

- Answer generation prompt.
- Chat response module.
- Standard factual answer format.

### Acceptance Criteria

- Every factual answer cites an approved source.
- Answers are concise and do not include unsupported assumptions.
- The assistant mentions the scheme name in scheme-specific answers.
- Missing information is handled conservatively.

## Phase 10: Citation Validation

### Goals

Ensure answers are supported by approved retrieved source chunks.

### Tasks

- Check that every factual answer includes a citation.
- Validate cited sources against the approved source list.
- Confirm that the generated answer is based on retrieved chunks.
- Replace invalid answers with a safe fallback.

### Deliverables

- Citation validator.
- Approved source validation logic.
- Safe fallback response.

### Acceptance Criteria

- Answers without citations are not returned.
- Citations must refer to approved official SBI Mutual Fund documents.
- Unsupported generated values are blocked.

## Phase 11: Chat Interface or API

### Goals

Expose the chatbot through a usable interface.

### Tasks

- Build a simple chat API or web interface.
- Connect the interface to classifier, normalization, retrieval, generation, and citation validation.
- Display concise answers and citations clearly.
- Handle errors gracefully.

### Deliverables

- Chat endpoint or web UI.
- End-to-end chatbot flow.
- Error handling.

### Acceptance Criteria

- Users can ask factual questions about supported SBI schemes.
- Users receive concise factual answers with citations.
- Advice questions receive a refusal response.

## Phase 12: Testing and Evaluation

### Goals

Verify factual accuracy, citation behavior, retrieval quality, and refusal behavior.

### Tasks

- Create test cases for each supported scheme.
- Create test cases for each supported field.
- Add refusal tests for advice and recommendation questions.
- Add retrieval tests for TER and factsheet questions.
- Add missing-information tests.
- Manually review generated responses for accuracy and concision.

### Deliverables

- Automated tests.
- Manual evaluation checklist.
- Test question set.

### Acceptance Criteria

- All supported factual questions return source-cited answers.
- Advice questions are refused.
- Missing facts are not invented.
- TER queries retrieve the TER source.
- Factsheet queries retrieve the relevant factsheet source.

## Phase 13: Deployment and Monitoring

### Goals

Prepare the chatbot for production or demo use.

### Tasks

- Package the application for deployment.
- Add startup checks for source documents and vector index.
- Log queries, retrieval results, and refusal decisions without storing sensitive personal data.
- Monitor unanswered queries and retrieval failures.
- Define a process for updating source documents and rebuilding the index.

### Deliverables

- Deployment-ready application.
- Startup validation.
- Monitoring/logging setup.
- Source update and reindexing process.

### Acceptance Criteria

- The application starts only when approved sources and vector index are available.
- Source document updates can be reindexed reliably.
- Logs help identify retrieval gaps and unsupported question types.

## Suggested Build Order

1. Project setup
2. Source document collection
3. Parsing and ingestion
4. Chunking and metadata validation
5. Embeddings and vector store
6. Question classifier
7. Query normalization
8. Retrieval pipeline
9. Answer generation
10. Citation validation
11. Chat interface or API
12. Testing and evaluation
13. Deployment and monitoring

## MVP Scope

The first working version should include:

- Approved source document ingestion.
- Chunking with citation metadata.
- Vector search.
- Advice-question refusal.
- Factual answer generation with citations.
- Basic chat interface or API.
- Test cases for all supported schemes and fields.

## Non-Goals

The system should not:

- Provide investment recommendations.
- Rank funds by suitability.
- Use unofficial sources.
- Answer from model memory.
- Generate answers without citations.
- Support schemes outside the approved list unless new official sources are added and indexed.
