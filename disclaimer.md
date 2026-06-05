# Chatbot Scope & Disclaimer Policy

The **SBI Mutual Fund FAQ Assistant** is built to operate under a strict **Facts-Only Policy**. It is designed to act as an information retrieval system rather than a financial advisor.

---

## 1. Scope of Operations
The assistant is restricted to answering factual questions about three specific mutual fund schemes:
1. **SBI Flexicap Fund**
2. **SBI ELSS Tax Saver Fund**
3. **SBI Large Cap Fund**

All factual answers are backed directly by official mutual fund documents (factsheets and TER reports) and include standard page or sheet-row citations.

---

## 2. Investment Advice Refusal
The assistant is prohibited from providing:
* Investment advice or personalized recommendations.
* Buy, sell, hold, or redemption opinions.
* Fund comparisons for suitability.
* Extrapolations or projections of future performance.

When asked advice-seeking questions (e.g., *"Is this fund good for me?"*, *"Should I buy ELSS?"*), the assistant will immediately block the request and return the standard disclaimer snippet:

> **"I cannot provide investment advice or recommendations. I can only provide factual information from official SBI Mutual Fund documents."**

---

## 3. Data Restrictions
The chatbot is designed to prevent model-memory hallucinations. It is instructed to:
1. Ground every answer on retrieved facts.
2. Refuse to answer questions outside the official ingested sources.
3. Fall back to: *"I could not find this information in the available approved SBI Mutual Fund sources."* if the query pertains to unsupported fields (such as daily NAV or historical returns).
