# Context

## Problem Statement

Build a facts-only Mutual Fund FAQ Assistant for SBI Mutual Fund.

The assistant should answer factual questions related to the following schemes:

1. SBI Flexicap Fund
2. SBI ELSS Tax Saver Fund
3. SBI Large Cap Fund

The goal is to build a Retrieval-Augmented Generation (RAG) based chatbot that retrieves information from official SBI Mutual Fund source documents and generates accurate, concise, factual answers.

## Supported Question Types

The assistant should answer factual questions such as:

- What is the expense ratio?
- What is the exit load?
- What is the minimum SIP amount?
- What is the minimum investment amount?
- What is the benchmark index?
- What is the risk level or riskometer?
- What is the lock-in period?
- What is the investment objective?

## Required Behavior

The assistant must:

- Use only official SBI Mutual Fund documents as sources.
- Provide a source citation with every answer.
- Give concise factual responses.
- Answer only based on retrieved source content.
- Avoid assumptions or unsupported claims.
- Refuse investment advice questions.

## Refusal Scope

The assistant must refuse questions that ask for investment advice, recommendations, comparisons, or buy/sell decisions.

Examples of questions to refuse:

- Should I invest?
- Which fund is better?
- Should I buy?
- Should I sell?
- Which scheme should I choose?
- Is this fund good for me?

For these questions, the assistant should explain that it can provide factual information only and cannot provide investment advice.

## Data Sources

The RAG system must use only the following official SBI Mutual Fund documents:

1. SBI Flexicap Fund Factsheet, April 2026
2. SBI ELSS Tax Saver Fund Factsheet, April 2026
3. SBI Large Cap Fund Factsheet, April 2026
4. SBI Total Expense Ratio (TER) Data File

## Answering Rules

Every answer should:

- Be short and factual.
- Include a source citation.
- Mention the scheme name when answering scheme-specific questions.
- State when information is not found in the available sources.
- Avoid giving financial advice or personalized recommendations.

## Example Response Style

Question: What is the minimum SIP amount for SBI Flexicap Fund?

Answer: The minimum SIP amount for SBI Flexicap Fund is the amount stated in the official April 2026 factsheet. Source: SBI Flexicap Fund Factsheet, April 2026.

Question: Should I invest in SBI Large Cap Fund?

Answer: I cannot provide investment advice or recommendations. I can only provide factual information from official SBI Mutual Fund documents.
