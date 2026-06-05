import streamlit as st
import requests
from typing import Optional

from sbi_fund_faq.config import get_settings
from sbi_fund_faq.retrieval.retriever import Retriever
from sbi_fund_faq.chatbot import generate_answer, validate_answer

# Load settings
settings = get_settings()
api_url = f"http://{settings.host}:{settings.port}/query"

# Title & Subtitle
st.title("SBI Mutual Fund FAQ Assistant")
st.caption("Facts-only. No investment advice.")

# Description
st.markdown("""
This assistant answers factual questions about the following official SBI Mutual Fund schemes:
1. **SBI Flexicap Fund**
2. **SBI ELSS Tax Saver Fund**
3. **SBI Large Cap Fund**
""")

# Sample questions
sample_questions = [
    "What is the exit load of SBI Flexicap Fund?",
    "What is the expense ratio of SBI Large Cap Fund?",
    "Should I invest in SBI ELSS Tax Saver Fund?"
]

st.write("### Try a Sample Question:")
cols = st.columns(len(sample_questions))
selected_question = None

for i, q in enumerate(sample_questions):
    if cols[i].button(q, key=f"btn_{i}"):
        selected_question = q

# Input box
query = st.text_input("Ask a question:", value=selected_question or "", placeholder="e.g., What is the benchmark index of SBI Large Cap Fund?")

if st.button("Ask", type="primary") or selected_question:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving facts and generating answer..."):
            # Attempt to call the FastAPI backend via HTTP first
            backend_success = False
            response_data = {}
            try:
                resp = requests.post(api_url, json={"question": query}, timeout=5)
                if resp.status_code == 200:
                    response_data = resp.json()
                    backend_success = True
            except Exception:
                pass

            if not backend_success:
                # Standalone Mode: Fallback to direct library calls (useful if FastAPI server is not running)
                try:
                    retriever = Retriever(settings)
                    result = retriever.retrieve(query)

                    if result.fallback_response is not None:
                        is_advice = result.classification.is_advice
                        is_ambiguous = result.normalized_query.is_ambiguous_scheme or (
                            not is_advice and result.normalized_query.scheme_name is None and "specify" in result.fallback_response
                        )
                        response_data = {
                            "answer": result.fallback_response,
                            "chunks": [],
                            "is_advice": is_advice,
                            "is_ambiguous": is_ambiguous
                        }
                    else:
                        generated = generate_answer(query, result.chunks, settings)
                        _, validated_answer = validate_answer(generated, result.chunks)
                        
                        response_chunks = [
                            {
                                "id": c.id,
                                "score": c.score,
                                "text": c.text,
                                "metadata": c.metadata
                            }
                            for c in result.chunks
                        ]
                        response_data = {
                            "answer": validated_answer,
                            "chunks": response_chunks,
                            "is_advice": False,
                            "is_ambiguous": False
                        }
                except Exception as e:
                    st.error(f"Error running pipeline in standalone mode: {e}")
                    response_data = {}

            # Display response
            if response_data:
                answer = response_data.get("answer", "")
                is_advice = response_data.get("is_advice", False)
                is_ambiguous = response_data.get("is_ambiguous", False)
                chunks = response_data.get("chunks", [])

                st.write("---")
                if is_advice:
                    st.info(answer)
                elif is_ambiguous:
                    st.warning(answer)
                else:
                    st.success(answer)
                    
                    if "Source:" in answer:
                        parts = answer.split("Source:")
                        citation = parts[-1].strip()
                        st.markdown(f"**Citation:** *{citation}*")
                    
                    if chunks:
                        with st.expander("Show Retrieved Chunks & Similarity Scores"):
                            for idx, chunk in enumerate(chunks):
                                citation_str = chunk['metadata'].get('citation', 'Unknown')
                                st.markdown(f"**Source {idx+1}:** {citation_str} *(Score: {chunk.get('score'):.4f})*")
                                st.code(chunk.get("text"))
                                st.markdown("---")
