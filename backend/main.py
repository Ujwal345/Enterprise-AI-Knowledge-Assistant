import os
import uuid
from io import BytesIO

import chromadb
import ollama

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pypdf import PdfReader

# ADD THIS HERE
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://host.docker.internal:11434"
)
ollama_client = ollama.Client(host=OLLAMA_HOST)

# 1. Initialize FastAPI
app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    description="RAG-based PDF question answering system",
    version="1.0.0"
)

#Prometheus Monitoring
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# 2. Initialize ChromaDB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

client = chromadb.PersistentClient(
    path=os.path.join(BASE_DIR, "chroma_db")
)

collection = client.get_or_create_collection(
    name="enterprise_documents"
)


# 3. Chat request model
class ChatRequest(BaseModel):
    question: str


# 4. Divide text into smaller chunks
def split_text(text, chunk_size=1000, overlap=150):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# 5. Home endpoint
@app.get("/")
def home():

    return {
        "message": "Enterprise AI Knowledge Assistant is running!"
    }


# 6. Health endpoint
@app.get("/health")
def health():

    return {
        "status": "healthy",
        "documents_stored": collection.count()
    }


# 7. PDF upload and vector storage
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")

    contents = await file.read()

    if not contents.startswith(b"%PDF-"):
        raise HTTPException(400, "Invalid PDF file")

    try:

        pdf = PdfReader(BytesIO(contents))

        all_chunks = []
        metadatas = []

        for page_number, page in enumerate(pdf.pages, start=1):

            page_text = page.extract_text() or ""

            page_chunks = split_text(page_text)

            for chunk in page_chunks:

                all_chunks.append(chunk)

                metadatas.append({
                    "source": file.filename,
                    "page": page_number
                })

        if not all_chunks:
            raise HTTPException(
                422,
                "No extractable text found in PDF"
            )

        # Generate embeddings
        embedding_response = ollama.embed(
            model="nomic-embed-text",
            input=all_chunks
        )

        embeddings = embedding_response["embeddings"]

        # Remove older version of same filename
        existing = collection.get(
            where={"source": file.filename}
        )

        if existing["ids"]:
            collection.delete(ids=existing["ids"])

        # Store chunks and embeddings in ChromaDB
        ids = [
            str(uuid.uuid4())
            for _ in all_chunks
        ]

        collection.add(
            ids=ids,
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return {
            "message": "PDF processed and stored successfully",
            "filename": file.filename,
            "total_pages": len(pdf.pages),
            "total_chunks": len(all_chunks)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            500,
            detail=f"PDF processing failed: {str(e)}"
        )


# 8. RAG-based question answering
@app.post("/chat")
def chat(request: ChatRequest):

    if collection.count() == 0:
        raise HTTPException(
            400,
            "Please upload a PDF before asking questions"
        )

    try:

        # Convert question into an embedding
        query_embedding = ollama_client.embed(
            model="nomic-embed-text",
            input=request.question,
        )["embeddings"][0]

        # Search relevant PDF chunks
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(3, collection.count())
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        context = "\n\n".join(
            f"Source: {meta['source']}, Page: {meta['page']}\n{doc}"
            for doc, meta in zip(documents, metadatas)
        )

        # Generate answer using retrieved context
        response = ollama_client.chat(
            model="qwen2.5:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question using only "
                        "the provided PDF context. If the answer "
                        "is not present in the context, say that "
                        "the uploaded documents do not contain "
                        "enough information. Do not invent facts."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"PDF Context:\n{context}\n\n"
                        f"Question: {request.question}"
                    )
                }
            ],
        )

        return {
            "question": request.question,
            "answer": response["message"]["content"],
            "sources": metadatas
        }

    except Exception as e:
        raise HTTPException(
            500,
            detail=f"Question answering failed: {str(e)}"
        )
