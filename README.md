
# Enterprise AI Knowledge Assistant

An AI-powered knowledge assistant that allows users to upload PDF documents and ask questions. It uses Retrieval-Augmented Generation (RAG) to generate answers based on the uploaded documents.

## Features

- Upload and process PDF documents
- Extract and split document text into chunks
- Generate embeddings using Ollama
- Store and retrieve document embeddings using ChromaDB
- Ask questions and receive context-based answers
- FastAPI backend
- Streamlit frontend
- Docker and Docker Compose support
- Kubernetes deployment manifests
- Prometheus metrics and Grafana monitoring
- GitHub Actions CI pipeline

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | Streamlit |
| LLM | Ollama, Qwen 2.5 3B |
| Embeddings | Ollama, nomic-embed-text |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes |
| Monitoring | Prometheus, Grafana |
| CI/CD | GitHub Actions |

## Project Structure

```text
enterprise-ai-assistant/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── documents/
├── monitoring/
│   └── prometheus.yml
├── k8s/
│   ├── backend-deployment.yaml
│   └── frontend-deployment.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Python 3.11
- Docker Desktop
- Kubernetes enabled in Docker Desktop
- Ollama installed
- Git

## AI Models

Download the required models using Ollama:

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Ujwal345/Enterprise-AI-Knowledge-Assistant.git
cd Enterprise-AI-Knowledge-Assistant
```

### 2. Start Ollama

Make sure Ollama is running and both required models are available.

### 3. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Start the backend

```bash
uvicorn main:app --reload
```

Backend API: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Backend welcome endpoint |
| GET | `/health` | Health check |
| POST | `/upload-pdf` | Upload and process PDF |
| POST | `/chat` | Ask questions |
| GET | `/metrics` | Prometheus metrics |

## Docker Deployment

Build and start the application services:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

Stop services:

```bash
docker compose down
```

## Kubernetes Deployment

Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/
```

Check deployments and pods:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

Access the frontend:

```bash
kubectl port-forward service/enterprise-ai-frontend 8502:8501
```

Open `http://localhost:8502` in your browser.

## Monitoring

Prometheus collects backend metrics from the `/metrics` endpoint.

Prometheus: `http://localhost:9090`

Grafana: `http://localhost:3000`

The Grafana dashboard includes:

- Backend CPU usage
- Backend memory usage
- Backend availability status

## CI Pipeline

GitHub Actions runs when code is pushed to the `main` branch or a pull request targets `main`.

The workflow performs:

- Repository checkout
- Python setup
- Backend dependency installation
- Python syntax validation
- Backend Docker image build
- Frontend Docker image build

## Future Improvements

- Automated Kubernetes deployment from CI/CD
- Authentication and role-based access
- Support for additional document formats
- Improved logging and alerting

## Author

**Ujwal Dhomne**

Enterprise AI Knowledge Assistant – Integrated Mini Project
