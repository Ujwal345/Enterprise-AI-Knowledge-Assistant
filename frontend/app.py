import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🤖"
)

st.title("🤖 Enterprise AI Knowledge Assistant")
st.write("Upload PDFs and ask questions using AI.")

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if st.button("Upload PDF"):
    if uploaded_file:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        try:
            response = requests.post(
                f"{API_URL}/upload-pdf",
                files=files,
                timeout=300
            )

            if response.ok:
                st.success("PDF uploaded successfully!")
                st.json(response.json())
            else:
                st.error(response.text)

        except requests.RequestException as e:
            st.error(str(e))

st.subheader("Ask your document")

question = st.text_input("Enter your question")

if st.button("Ask AI"):
    if question:
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"question": question},
                timeout=300
            )

            if response.ok:
                result = response.json()
                st.write("### AI Answer")
                st.write(result["answer"])
                st.write("### Sources")
                st.json(result["sources"])
            else:
                st.error(response.text)

        except requests.RequestException as e:
            st.error(str(e))
