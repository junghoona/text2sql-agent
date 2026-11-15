"""Streamlit chat UI: streamlit run app.py"""
import streamlit as st

from t2s import db
from t2s.agent import ask

st.set_page_config(page_title="Text-to-SQL Agent", page_icon="🔎")
st.title("🔎 Text-to-SQL Agent")

with st.sidebar:
    st.subheader("Schema")
    st.code(db.get_schema(), language="sql")
    if st.button("Clear chat"):
        st.session_state.clear()

st.session_state.setdefault("history", [])   # (role, text) for display
st.session_state.setdefault("messages", [])  # full API transcript

for role, text in st.session_state.history:
    st.chat_message(role).markdown(text)

if q := st.chat_input("Ask a question about your data"):
    st.chat_message("user").markdown(q)
    st.session_state.history.append(("user", q))
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("assistant"), st.spinner("Thinking..."):
        answer = ask(st.session_state.messages)
        st.markdown(answer)
    st.session_state.history.append(("assistant", answer))
