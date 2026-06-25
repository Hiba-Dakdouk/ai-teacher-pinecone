# AI Teacher 🎓

An intelligent tutoring chatbot that teaches students Artificial Intelligence using a full RAG (Retrieval-Augmented Generation) pipeline. The system guides students toward answers through questions and hints rather than giving direct responses.

Live demo: ai-teacher-pinecone.vercel.app
---

## What It Does

The owner can upload some permanent course materials, also students can upload their course materials (PDF documents) and have a conversation with an AI teacher that:
- Answers questions **based on the uploaded material** using RAG
- Never gives direct answers: it rather guides students to discover answers themselves
- Stays strictly on topic: it redirects off-topic questions back to AI learning
- Maintains full conversation context across the session

---

## Why This Is Non-Trivial

This project implements a proper RAG pipeline:

1. Uploaded PDFs are parsed, chunked with overlap, and embedded into vectors
2. Each student message triggers a semantic similarity search across the knowledge base
3. Only the 3 most relevant chunks of each of the owner's and student's documents are retrieved and injected into the prompt
4. Claude generates a response grounded in the course material

The system is fully containerized with Docker and deployed to production using a cloud-native vector database (Pinecone), making it usable from anywhere rather than only on a local machine.
---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Anthropic Claude (claude-sonnet) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Database | Pinecone |
| Backend | Python, FastAPI, Pydantic |
| PDF Parsing | pdfplumber |
| Frontend | React, Vite, Axios |
| Markdown | Renderingreact-markdown |
| Containerization | Docker |
| Deployment |Vercel (frontend), Railway (backend) |
| Environment | python-dotenv |
| Markdown Rendering | react-markdown |

---

## Architecture

```
User message
     ↓
Frontend (React)
     ↓ POST /chat
Backend (FastAPI)
     ↓
Embed query → Pinecone similarity search → retrieve top 3 chunks
     ↓
Inject chunks into system prompt
     ↓
Anthropic Claude API
     ↓
Streaming reply → Frontend
```

**Indexing pipeline** (runs on PDF upload):
```
PDF → pdfplumber → raw text → chunk (500 chars, 50 overlap)
    → OpenAI embeddings → Pinecone upsert (tagged with source metadata)
```

**Retrieval pipeline** (runs on every message):
```
User question → embed → Pinecone similarity search across the
    entire index (no source filtering at query time)
→ top 3 matching chunks → augmented system prompt → Claude
```
Owner-uploaded and student-uploaded documents are stored in the same Pinecone index, tagged with a source metadata field ("owner_docs" or "student_docs").
---

## Project Structure

```
ai-teacher-pinecone/
├── backend/
│   ├── main.py          # FastAPI routes (/chat, /upload, /admin/upload)
│   ├── chat.py          # Claude API logic + RAG injection
│   ├── rag.py           # Full RAG pipeline (chunk, embed, store, search)
│   ├── pdf_parser.py    # PDF text extraction
│   ├── models.py        # Pydantic data models
│   ├── requirements.txt
│   ├── Dockerfile        # Container build definition
│   ├── .dockerignore
│   └── .env             # API keys (not committed)
└── frontend/
    ├── src/
    │   ├── App.jsx           # Main component — state and chat logic
    │   ├── DocumentUpload.jsx # PDF upload component
    │   ├── api.js            # HTTP communication layer
    │   ├── main.jsx          # React entry point
    │   └── App.css           # Styling
    └── package.json
```

---

## Setup & Running

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- OpenAI API key ([platform.openai.com](https://platform.openai.com))
- Pinecone API key and index (pinecone.io) — index configured with 1536 dimensions, cosine metric

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
```
### Backend — Local (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the server:
```bash
uvicorn main:app --reload --port 8000
```
### Backend — With Docker

```bash
cd backend
docker build -t ai-teacher-backend .
docker run -p 8000:8000 --env-file .env ai-teacher-backend
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Deployment

- **Frontend** is deployed on **Vercel**, built directly from the `frontend/` directory.
- **Backend** is deployed on **Railway**, built from the Dockerfile in `backend/`, with environment variables (API keys) set in Railway's dashboard.
- **Vector storage** runs on **Pinecone's cloud infrastructure**.

---

## How to Use

**As owner/admin:**
1. Go to http://localhost:8000/docs
2. Use POST /admin/upload to pre-load AI course materials
3. These documents are permanent and available to all students

**As student:**
1. Open the app at http://localhost:5173
2. Optionally upload a personal PDF using the upload button
3. Ask questions — the teacher answers from both owner and student documents
---

## Key Design Decisions

**Why RAG instead of full document injection?**
Injecting a full document into every prompt is expensive and fails for large documents. RAG retrieves only what's relevant — reducing token cost by ~100x and removing document size limits.

**Why OpenAI embeddings with Anthropic Claude?**
OpenAI's `text-embedding-3-small` is the industry standard for Embeddings. Claude handles generation. Best tool for each job.

**Why Pinecone instead of a local vector database?**
Local vector databases (e.g. ChromaDB) persist data to disk, which works for local development but breaks on most cloud platforms. Data is wiped on every restart or redeploy. Pinecone stores vectors in the cloud, so the knowledge base survives deployments and server restarts.

**Why metadata tagging instead of separate collections?**
Pinecone's free tier provides a single index per project. Rather than requiring a paid multi-index setup, owner and student documents are tagged with a `source` field in metadata so they coexist in one index. 

**Why Docker?**
Containerizing the backend ensures the exact same environment runs locally and in production, eliminating "works on my machine" issues.

**Why a Socratic system prompt?**
A teacher that gives direct answers produces passive learners. Guiding students to discover answers themselves produces deeper understanding and retention — the core pedagogical principle behind this project.

**How off-topic questions are handled?**
A strict system prompt defines the allowed domain — AI, Machine Learning, Data Science, and directly related mathematics and programming concepts. Claude is instructed to reject questions outside this domain regardless of whether the answer exists in uploaded documents.

---

## Limtations/Future work

**No per-student document isolation**
**No source-based filtering at query time**

---


