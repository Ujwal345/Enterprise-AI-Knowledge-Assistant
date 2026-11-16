import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Enterprise AI Knowledge Assistant")
st.caption("Upload PDF documents and ask questions using AI.")

# PDF upload section
st.sidebar.header("Upload Documents")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF document",
    type=["pdf"]
)

if st.sidebar.button("Upload PDF"):
    if uploaded_file is not None:
        try:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            response = requests.post(
                f"{API_URL}/upload-pdf",
                files=files,
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                st.sidebar.success("PDF uploaded successfully!")
                st.sidebar.write(result)
            else:
                st.sidebar.error(response.text)

        except requests.RequestException as e:
            st.sidebar.error(f"Backend connection failed: {e}")
    else:
        st.sidebar.warning("Please select a PDF first.")

# Chat section
st.subheader("Ask your documents")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask something about your PDF...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"question": question},
                    timeout=300
                )

                response.raise_for_status()
                result = response.json()

                answer = result["answer"]
                st.write(answer)

                st.caption("Sources:")
                for source in result.get("sources", []):
                    st.write(
                        f"- {source['source']} "
                        f"(Page {source['page']})"
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.RequestException as e:
                st.error(f"Unable to get answer: {e}")
