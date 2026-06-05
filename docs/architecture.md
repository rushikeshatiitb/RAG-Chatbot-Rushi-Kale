# Architecture

## Overview

The SBI Mutual Fund FAQ Assistant is a Retrieval-Augmented Generation (RAG) chatbot that answers only factual questions about selected SBI Mutual Fund schemes. It uses official SBI Mutual Fund documents as the only knowledge source and refuses investment advice or recommendation-style questions.

## Supported Schemes

The assistant supports factual questions for:

1. SBI Flexicap Fund
2. SBI ELSS Tax Saver Fund
3. SBI Large Cap Fund

## Source Documents

The system should ingest and retrieve information only from:

1. SBI Flexicap Fund Factsheet, April 2026
2. SBI ELSS Tax Saver Fund Factsheet, April 2026
3. SBI Large Cap Fund Factsheet, April 2026
4. SBI Total Expense Ratio (TER) Data File

No external websites, unofficial summaries, or model-only knowledge should be used for answering.

## High-Level Flow

```text
User Question
    |
    v
Question Classifier
    |
    |-- Investment advice question --> Refusal Response
    |
    v
Query Normalization
    |
    v
Retriever
    |
    v
Relevant Source Chunks
    |
    v
Answer Generator
    |
    v
Citation Validator
    |
    v
Final Factual Answer with Source Citation
```

## Core Components

### 1. Document Ingestion

The ingestion pipeline loads the official SBI Mutual Fund source documents and prepares them for retrieval.

Responsibilities:

- Load factsheets and TER data files.
- Extract text and structured values from source documents.
- Preserve source metadata such as document name, scheme name, section, page number, and date.
- Split documents into searchable chunks.
- Store each chunk with citation metadata.

Recommended metadata fields:

- `source_name`
- `scheme_name`
- `document_type`
- `document_month`
- `page_number`
- `section`
- `chunk_text`

### 2. Chunking Strategy

Chunks should be small enough for precise retrieval but large enough to retain context.

Recommended approach:

- Use section-aware chunking where possible.
- Keep factsheet fields such as investment objective, benchmark, exit load, riskometer, and minimum application amount together.
- Keep TER data mapped clearly to scheme and plan.
- Attach source metadata to every chunk.

### 3. Vector Store

The vector store stores embedded document chunks for semantic retrieval.

Responsibilities:

- Store embeddings for official source chunks.
- Support similarity search against user questions.
- Return top matching chunks with metadata.

The vector store must contain only chunks from approved SBI Mutual Fund documents.

### 4. Question Classifier

The classifier decides whether the user question is factual or advice-seeking.

Factual questions should continue to retrieval.

Examples:

- What is the exit load for SBI Flexicap Fund?
- What is the benchmark index for SBI Large Cap Fund?
- What is the lock-in period for SBI ELSS Tax Saver Fund?

Advice or recommendation questions should be refused before retrieval or generation.

Examples:

- Should I invest in SBI Flexicap Fund?
- Which fund is better?
- Should I buy or sell?
- Which scheme should I choose?

### 5. Query Normalization

Query normalization improves retrieval accuracy by mapping user wording to known fund fields.

Examples:

- `risk level` maps to `riskometer`
- `minimum investment` maps to `minimum application amount`
- `SIP minimum` maps to `minimum SIP amount`
- `expense ratio` maps to `TER`

The normalized query should preserve the original user intent.

### 6. Retrieval

The retriever searches the vector store for relevant official-source chunks.

Retrieval should prioritize:

- Matching scheme name.
- Matching field type, such as expense ratio, exit load, benchmark, or investment objective.
- Current approved document version.
- Chunks with clear citation metadata.

If no reliable source chunk is found, the assistant should say that the information was not found in the available official sources.

### 7. Answer Generation

The answer generator creates a concise factual response from retrieved chunks only.

Rules:

- Do not answer from model memory.
- Do not infer missing values.
- Do not compare funds unless the question asks for factual side-by-side fields and the retrieved sources support it.
- Mention the scheme name in scheme-specific answers.
- Include a source citation in every answer.

Example format:

```text
The exit load for SBI Flexicap Fund is [value]. Source: SBI Flexicap Fund Factsheet, April 2026.
```

### 8. Citation Validator

Before returning the final answer, the system should verify that:

- The answer includes at least one source citation.
- The cited source is one of the approved SBI Mutual Fund documents.
- The factual value in the answer is supported by the retrieved chunk.

If citation validation fails, the assistant should not return the generated answer. It should instead return a safe fallback stating that the information was not found in the available official sources.

## Refusal Behavior

For investment advice questions, the assistant should return a refusal response.

Example:

```text
I cannot provide investment advice or recommendations. I can only provide factual information from official SBI Mutual Fund documents.
```

The refusal response does not need retrieval because it does not answer a fund fact.

## Data Model

Each indexed chunk should follow a structure similar to:

```json
{
  "id": "sbi-flexicap-factsheet-apr-2026-page-3-chunk-2",
  "source_name": "SBI Flexicap Fund Factsheet",
  "scheme_name": "SBI Flexicap Fund",
  "document_type": "Factsheet",
  "document_month": "April 2026",
  "page_number": 3,
  "section": "Fund Details",
  "chunk_text": "..."
}
```

## Prompting Rules

The system prompt should instruct the model to:

- Act as a facts-only SBI Mutual Fund FAQ assistant.
- Use only retrieved context.
- Provide concise factual answers.
- Include citations.
- Refuse investment advice and recommendations.
- Say when information is not found in the available sources.

## Evaluation Checklist

The assistant should be tested for:

- Correct answer retrieval for each supported field.
- Citation presence in every factual answer.
- Refusal of advice questions.
- No unsupported claims when retrieval fails.
- Correct scheme detection.
- Correct handling of TER or expense ratio queries.
- Concise answer style.

## Example Test Cases

| User Question | Expected Behavior |
| --- | --- |
| What is the benchmark index for SBI Large Cap Fund? | Return factual answer with factsheet citation. |
| What is the expense ratio of SBI Flexicap Fund? | Retrieve TER data and return factual answer with TER source citation. |
| What is the lock-in period for SBI ELSS Tax Saver Fund? | Return factual answer with factsheet citation. |
| Should I invest in SBI ELSS Tax Saver Fund? | Refuse investment advice. |
| Which fund is better, SBI Flexicap or SBI Large Cap? | Refuse recommendation/comparison advice. |

## Key Design Principle

The assistant should be conservative. If the answer is not directly supported by official retrieved source content, it should not answer.
