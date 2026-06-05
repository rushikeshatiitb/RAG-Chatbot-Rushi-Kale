"""Answer generation module using LLMs or local mock fallback."""

import os
import re
from typing import TYPE_CHECKING, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from sbi_fund_faq.config import Settings, get_settings

if TYPE_CHECKING:
    from sbi_fund_faq.retrieval.retriever import RetrievedChunk

NOT_FOUND_RESPONSE = "I could not find this information in the available approved SBI Mutual Fund sources."

SYSTEM_PROMPT_TEMPLATE = """You are a facts-only Mutual Fund FAQ Assistant for SBI Mutual Fund.
Your goal is to answer the user's question accurately, using ONLY the facts provided in the official source chunks below.

Here are the retrieved official source chunks:
---
{context}
---

Rules:
1. Base your answer ONLY on the official source chunks provided. Do NOT assume, extrapolate, or use model memory for facts not in the chunks.
2. If the answer cannot be found in the provided chunks, respond EXACTLY with:
"I could not find this information in the available approved SBI Mutual Fund sources."
3. Keep your response extremely short, direct, and factual (maximum 2-3 sentences).
4. You MUST include a citation at the end of your answer in the EXACT format:
Source: <citation>
where <citation> matches the "citation" field in the metadata of the chunk you used.
5. In scheme-specific answers, explicitly mention the scheme name (e.g., "SBI Flexicap Fund", "SBI ELSS Tax Saver Fund", or "SBI Large Cap Fund").
6. Do NOT provide investment advice, recommendations, comparisons (unless purely factual based on chunks), or buy/sell decisions.
"""


def generate_answer(
    question: str,
    chunks: list["RetrievedChunk"],
    settings: Optional[Settings] = None,
) -> str:
    """Generate a factual answer using retrieved chunks, or fall back to mock mode if API key is missing."""
    settings = settings or get_settings()
    
    if not chunks:
        return NOT_FOUND_RESPONSE

    provider = settings.model_provider.lower()
    api_key = None
    base_url = None
    model_name = settings.chat_model

    if provider == "groq":
        api_key = settings.groq_api_key or os.environ.get("GROQ_API_KEY")
        base_url = settings.groq_api_base
    elif provider == "openai":
        api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
        base_url = None

    # Fallback checking: if the requested provider has no key, check for the other provider's key
    if not api_key:
        if provider == "groq" and (settings.openai_api_key or os.environ.get("OPENAI_API_KEY")):
            api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
            base_url = None
            model_name = "gpt-4o-mini"
        elif provider == "openai" and (settings.groq_api_key or os.environ.get("GROQ_API_KEY")):
            api_key = settings.groq_api_key or os.environ.get("GROQ_API_KEY")
            base_url = settings.groq_api_base
            model_name = "llama-3.3-70b-versatile"

    if api_key:
        try:
            # Format context from chunks
            context_blocks = []
            for chunk in chunks:
                citation = chunk.metadata.get("citation", "Unknown Source")
                context_blocks.append(
                    f"Chunk ID: {chunk.id}\n"
                    f"Citation: {citation}\n"
                    f"Content: {chunk.text}\n"
                )
            context_text = "\n---\n".join(context_blocks)
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)

            llm = ChatOpenAI(
                model=model_name,
                temperature=0.0,
                api_key=api_key,
                base_url=base_url,
            )
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=question),
            ]
            response = llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            # Log and proceed to mock fallback rather than raising
            print(f"Error calling LLM API: {e}. Falling back to mock generation.")
            pass

    return generate_mock_answer(question, chunks)


def generate_mock_answer(question: str, chunks: list["RetrievedChunk"]) -> str:
    """Local developer mock answer generator when OPENAI_API_KEY is missing."""
    if not chunks:
        return NOT_FOUND_RESPONSE

    top_chunk = chunks[0]
    citation = top_chunk.metadata.get("citation", "Unknown Source")
    scheme_name = top_chunk.metadata.get("scheme_name") or "SBI Mutual Fund Scheme"
    text = top_chunk.text.strip()
    text_lower = text.lower()
    q_lower = question.lower()

    # Determine query type based on question first, fallback to text keywords
    is_exit_load = "exit load" in q_lower or ("exit load" in text_lower and not any(k in q_lower for k in ["expense ratio", "ter", "benchmark", "lock-in", "lock in", "sip"]))
    is_ter = "expense ratio" in q_lower or "ter" in q_lower or (("total ter" in text_lower or "expense ratio" in text_lower) and not any(k in q_lower for k in ["exit load", "benchmark", "lock-in", "lock in", "sip"]))
    is_benchmark = "benchmark" in q_lower or ("benchmark" in text_lower and not any(k in q_lower for k in ["exit load", "expense ratio", "ter", "lock-in", "lock in", "sip"]))
    is_sip = "sip" in q_lower or (("minimum sip" in text_lower or "sip" in text_lower) and not any(k in q_lower for k in ["exit load", "expense ratio", "ter", "benchmark", "lock-in", "lock in"]))
    is_lockin = "lock-in" in q_lower or "lock in" in q_lower or (("lock-in" in text_lower or "lock in" in text_lower) and not any(k in q_lower for k in ["exit load", "expense ratio", "ter", "benchmark", "sip"]))
    is_risk = "riskometer" in q_lower or "risk level" in q_lower or "risk" in q_lower or (("riskometer" in text_lower or "risk level" in text_lower or "risk" in text_lower) and not any(k in q_lower for k in ["exit load", "expense ratio", "ter", "benchmark", "sip", "lock-in", "lock in"]))

    if is_exit_load:
        match = re.search(r"Exit Load:\s*(.*?)(?=\s*•|\Z)", text, re.IGNORECASE)
        details = match.group(1).strip() if match else text
        details = re.sub(r"\s+", " ", details)
        # Handle empty/bullet load case
        if not details or details.startswith("•") or len(details) < 3:
            match_fallback = re.search(r"Exit Load:\s*•\s*(.*?)(?=\s*•|\Z)", text, re.IGNORECASE)
            if match_fallback:
                details = match_fallback.group(1).strip()
                details = re.sub(r"\s+", " ", details)
        return f"For {scheme_name}, the Exit Load is: {details} Source: {citation}"

    elif is_ter:
        match = re.search(
            r"Regular Plan Total TER\s*([\d\.]+%?);\s*Direct Plan Total TER\s*([\d\.]+%?)",
            text,
            re.IGNORECASE,
        )
        if match:
            reg, direct = match.group(1), match.group(2)
            date_match = re.search(r"on\s+(\d{4}-\d{2}-\d{2})", text)
            date_str = f" as of {date_match.group(1)}" if date_match else ""
            return (
                f"The Total Expense Ratio (TER) for {scheme_name}{date_str} is "
                f"{reg} for the Regular Plan and {direct} for the Direct Plan. Source: {citation}"
            )
        return f"The Total Expense Ratio (TER) details for {scheme_name} are: {text} Source: {citation}"

    elif is_benchmark:
        match = re.search(r"Benchmark:\s*(.*?)(?=\s*•|\Z)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"First Tier Benchmark:\s*(.*?)(?=\s*•|\Z)", text, re.IGNORECASE)
        details = match.group(1).strip() if match else text
        details = re.sub(r"\s+", " ", details)
        return f"The benchmark index for {scheme_name} is {details} Source: {citation}"

    elif is_sip:
        return f"The minimum SIP requirements for {scheme_name} are detailed in the factsheet. Source: {citation}"

    elif is_lockin:
        match = re.search(r"(statutory lock-in of \d+ years|lock-in period of \d+ years|lock-in of \d+ years)", text, re.IGNORECASE)
        if match:
            return f"The lock-in period for {scheme_name} is: {match.group(1)}. Source: {citation}"
        return f"The lock-in period for {scheme_name} is specified in the factsheet. Source: {citation}"

    elif is_risk:
        return f"The risk level/riskometer of {scheme_name} is detailed in the factsheet. Source: {citation}"

    # General fallback text snippet
    snippet = text
    if len(snippet) > 150:
        snippet = snippet[:147] + "..."
    snippet = re.sub(r"\s+", " ", snippet)
    return f"Regarding {scheme_name}: {snippet} Source: {citation}"
