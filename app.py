import streamlit as st
from main import get_answer, generate_csv_from_answer

import pandas as pd


st.title("AI-Powered Natural Language SQL Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input (Enter to submit, Shift+Enter for newline)
question = st.chat_input("Ask your question (use ; for multiple queries)")

# When user asks something
if question:
    queries = [q.strip() for q in question.split(";") if q.strip()]

    for q in queries:
        # show user message
        st.session_state.messages.append({
            "role": "user",
            "content": q
        })

        with st.chat_message("user"):
            st.markdown(q)

        # process each query separately
        with st.chat_message("assistant"):
            with st.spinner("⏳ Thinking..."):
                answer = get_answer(q)

                st.markdown(answer)

                df = generate_csv_from_answer(answer)

        # store response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })

# SIDEBAR FULL REPORT DOWNLOAD (NEW)

with st.sidebar:
    st.header("📊 Export")

    if "messages" in st.session_state and st.session_state.messages:

        all_data = []

        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                all_data.append({
                    "response": msg["content"]
                })

        if all_data:
            df = pd.DataFrame(all_data)
            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download Full Report",
                data=csv,
                file_name="full_report.csv",
                mime="text/csv",
                key="sidebar_download"
            )
        else:
            st.info("No data yet.")
    else:
        st.info("Ask questions to generate report.")
