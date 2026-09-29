import os

import requests
import streamlit as st


API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Enterprise RAG Chatbot",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Enterprise Document Intelligence & RAG Chatbot")
st.caption("LangChain • FAISS • Transformer Embeddings • LLM • FastAPI")

with st.sidebar:
    st.header("Document ingestion")
    uploaded = st.file_uploader(
        "Upload PDF, DOCX, TXT or Markdown",
        type=["pdf", "docx", "txt", "md"],
    )

    if uploaded and st.button("Index document", use_container_width=True):
        try:
            response = requests.post(
                f"{API_URL}/api/v1/documents",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                timeout=180,
            )
            if response.ok:
                st.success(f"Indexed {uploaded.name}")
            else:
                st.error(response.text)
        except requests.RequestException as exc:
            st.error(f"API unavailable: {exc}")

    st.divider()
    st.header("Retrieval settings")
    top_k = st.slider("Top K", min_value=1, max_value=10, value=4)

st.subheader("Ask your enterprise documents")

question = st.text_area(
    "Question",
    placeholder="What is the annual leave policy?",
    height=100,
)

if st.button("Ask", type="primary", use_container_width=True) and question.strip():
    try:
        response = requests.post(
            f"{API_URL}/api/v1/chat",
            json={"question": question, "top_k": top_k},
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()

        st.markdown("### Answer")
        st.write(data["answer"])

        st.markdown("### Retrieved sources")
        for index, source in enumerate(data["sources"], start=1):
            location = (
                f"page {source['page_number']}"
                if source.get("page_number")
                else f"chunk {source.get('chunk_index', '?')}"
            )
            with st.expander(
                f"[Source {index}] {source['source']} • {location} • score={source['score']:.4f}"
            ):
                st.write(source["text"])

    except requests.HTTPError as exc:
        st.error(f"Request failed: {exc.response.text}")
    except requests.RequestException as exc:
        st.error(f"API unavailable: {exc}")
