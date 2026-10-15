# DocuRAG – AI Document Q&A Assistant

A small end-to-end AI Engineering project that lets users upload documents, index them with embeddings, store vectors in ChromaDB, and chat with the content using Retrieval-Augmented Generation (RAG).

## Tech Stack

- Frontend: React + Vite
- Backend: Python + FastAPI
- Vector DB: ChromaDB
- Embeddings: `BAAI/bge-m3`
- LLM: Gemini API or OpenRouter
- Document parsing: PyPDF + plain text
- RAG: custom chunking + semantic retrieval
- Guardrail: system-prompt grounding rules + no-answer fallback

## Features

- Upload PDF / TXT / MD documents
- Extract and chunk document text
- Create embeddings with BGE-M3
- Store vectors in local ChromaDB
- Semantic retrieval for user questions
- Generate grounded answers with citations
- Fallback when retrieved context is insufficient
- Simple React chat UI

## Architecture

Document -> Parser -> Chunker -> BGE-M3 Embedding -> ChromaDB

User Question -> BGE-M3 Query Embedding -> ChromaDB Retrieval -> Context -> LLM -> Answer + Sources

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
Swagger: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Environment Variables

See `backend/.env.example`.

For Gemini:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash
```

For OpenRouter:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=google/gemma-3-27b-it:free
```

Model availability changes over time, so replace the model name if needed.

## CV Description

**DocuRAG – AI Document Q&A Assistant**

Built a Retrieval-Augmented Generation (RAG) web application that indexes uploaded documents and answers user questions using retrieved context.

- Built document ingestion and indexing pipeline using FastAPI, ChromaDB, and BGE-M3 embeddings.
- Implemented semantic retrieval over document chunks for context-aware question answering.
- Integrated configurable Gemini/OpenRouter LLM APIs for grounded response generation.
- Added prompt-based guardrails, citation metadata, and no-answer fallback behavior.
- Developed a React frontend for document upload and conversational Q&A.

**Tech Stack:** Python, FastAPI, React, ChromaDB, BAAI/bge-m3, RAG, Gemini/OpenRouter API, Git
