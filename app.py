"""
app.py — Streamlit UI for the Business Case Analyzer
"""
import streamlit as st
import tempfile
import os
from comments import extract_comments, extract_body_text, format_comments_for_llm
from ingest import load_documents, chunk_documents
from rag import build_index, retrieve, format_context
from agent import ask_agent, get_summary

st.set_page_config(page_title="Business Case Analyzer", page_icon="📄")
st.title("📄 Business Case Analyzer")
st.caption("Upload business case docs → get AI-powered analysis + comment insights")

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Drop .docx or .pdf files here",
        type=["docx", "pdf"],
        accept_multiple_files=True
    )
    analyze_btn = st.button("🔍 Analyze Documents", type="primary", disabled=not uploaded_files)

# --- Process uploads ---
if analyze_btn and uploaded_files:
    with st.spinner("Processing documents..."):
        all_comments = []
        temp_dir = tempfile.mkdtemp()

        # Save uploaded files to temp dir
        for f in uploaded_files:
            path = os.path.join(temp_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            # Extract comments from .docx files
            if f.name.endswith(".docx"):
                all_comments.extend(extract_comments(path))

        # Load and chunk documents
        docs = load_documents(temp_dir)
        chunks = chunk_documents(docs)

        # Build vector index
        collection = build_index(chunks)

        # Store in session state
        st.session_state["collection"] = collection
        st.session_state["comments"] = all_comments
        st.session_state["comments_str"] = format_comments_for_llm(all_comments)
        st.session_state["doc_count"] = len(docs)
        st.session_state["chunk_count"] = len(chunks)
        st.session_state["ready"] = True
        st.session_state["chat_history"] = []

    st.success(f"✅ Loaded {len(docs)} docs → {len(chunks)} chunks | {len(all_comments)} comments found")
    if all_comments:
        st.markdown("### Extracted reviewer comments")
        for comment in all_comments:
            st.markdown(f"- **{comment['author']}** ({comment['date']}): {comment['text']}")
    else:
        st.warning("No reviewer comments were extracted from the uploaded Word documents.")

# --- Main area: Tabs ---
if st.session_state.get("ready"):
    tab_summary, tab_chat = st.tabs(["📊 Summary", "💬 Chat"])

    with tab_summary:
        if "summary" not in st.session_state:
            with st.spinner("Generating summary..."):
                top_chunks = retrieve(st.session_state["collection"], "overview summary objectives budget")
                context = format_context(top_chunks)
                st.session_state["summary"] = get_summary(context, st.session_state["comments_str"])
        st.markdown(st.session_state["summary"])

    with tab_chat:
        st.markdown(f"**{st.session_state['doc_count']}** documents indexed | **{st.session_state.get('chunk_count', 0)}** chunks | **{len(st.session_state['comments'])}** comments")

        # Display chat history
        for msg in st.session_state.get("chat_history", []):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if question := st.chat_input("Ask about your business cases..."):
            st.session_state["chat_history"].append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    top_chunks = retrieve(st.session_state["collection"], question)
                    context = format_context(top_chunks)
                    answer = ask_agent(question, context, st.session_state["comments_str"])
                st.markdown(answer)
                st.session_state["chat_history"].append({"role": "assistant", "content": answer})
else:
    st.info("👈 Upload business case documents in the sidebar to get started.")