# AI Teacher 🎓

An intelligent tutoring chatbot that teaches students Artificial Intelligence using a full RAG (Retrieval-Augmented Generation) pipeline. The system guides students toward answers through questions and hints rather than giving direct responses.

---

## What It Does

The owner can upload some permanent course materials, aslo students can upload their course materials (PDF documents) and have a conversation with an AI teacher that:
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

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Anthropic Claude (claude-sonnet) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Database | ChromaDB |
| Backend | Python, FastAPI, Pydantic |
| PDF Parsing | pdfplumber |
| Frontend | React, Vite, Axios |
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
Embed query → ChromaDB similarity search → retrieve top 3 chunks
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
    → OpenAI embeddings → ChromaDB storage
```

**Retrieval pipeline** (runs on every message):
```
User question → embed → cosine similarity search in both collections
→ top 3 chunks from owner_docs + top 3 chunks from student_docs
→ combined context → augmented system prompt → Claude
```

---

## Project Structure

```
ai-teacher/
├── backend/
│   ├── main.py          # FastAPI routes (/chat, /upload)
│   ├── chat.py          # Claude API logic + RAG injection
│   ├── rag.py           # Full RAG pipeline (chunk, embed, store, search)
│   ├── pdf_parser.py    # PDF text extraction
│   ├── models.py        # Pydantic data models
│   ├── requirements.txt
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
```

Run the server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

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

**Why ChromaDB?**
Zero-setup local vector database, perfect for development. The entire RAG logic is isolated in `rag.py` — swapping to Pinecone for production requires changing only that file.

**Why a Socratic system prompt?**
A teacher that gives direct answers produces passive learners. Guiding students to discover answers themselves produces deeper understanding and retention — the core pedagogical principle behind this project.

**How off-topic questions are handled?**
A strict system prompt defines the allowed domain — AI, Machine Learning, Data Science, and directly related mathematics and programming concepts. Claude is instructed to reject questions outside this domain regardless of whether the answer exists in uploaded documents.

---



