from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.schemas import ChatRequest, ChatResponse
from app.services.document_service import extract_document
from app.services.chunking import chunk_text
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

app = FastAPI(title="DocuRAG API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "indexed_chunks": vector_store.count(),
        "embedding_model": settings.embedding_model,
        "llm_provider": settings.llm_provider,
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()

    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT and MD files are supported.",
        )

    safe_name = f"{uuid4().hex}_{Path(file.filename).name}"
    output_path = UPLOAD_DIR / safe_name

    content = await file.read()
    output_path.write_bytes(content)

    try:
        pages = extract_document(output_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    all_chunks = []
    metadatas = []
    ids = []

    for page_data in pages:
        chunks = chunk_text(page_data["text"])

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{safe_name}:{page_data['page']}:{idx}"
            ids.append(chunk_id)
            all_chunks.append(chunk)
            metadatas.append(
                {
                    "source": file.filename,
                    "stored_file": safe_name,
                    "page": page_data["page"] if page_data["page"] else -1,
                    "chunk_index": idx,
                }
            )

    if not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No readable text was extracted from the document.",
        )

    embeddings = embedding_service.encode_documents(all_chunks)
    vector_store.add_chunks(ids, all_chunks, embeddings, metadatas)

    return {
        "message": "Document indexed successfully.",
        "filename": file.filename,
        "chunks_added": len(all_chunks),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    question = payload.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")

    if vector_store.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. Upload a document first.",
        )

    query_embedding = embedding_service.encode_query(question)
    result = vector_store.search(query_embedding, settings.top_k)

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    retrieved = []

    for doc, meta, distance in zip(documents, metadatas, distances):
        if distance <= settings.min_distance_threshold:
            retrieved.append(
                {
                    "text": doc,
                    "metadata": meta,
                    "distance": distance,
                }
            )

    if not retrieved:
        return ChatResponse(
            answer="I don't have enough information in the uploaded documents to answer that.",
            sources=[],
        )

    context_parts = []
    sources = []

    for i, item in enumerate(retrieved, start=1):
        meta = item["metadata"]
        page = meta.get("page", -1)
        page_label = None if page == -1 else page

        context_parts.append(
            f"[Source {i}] File: {meta['source']} | Page: {page_label}\n{item['text']}"
        )

        sources.append(
            {
                "source": meta["source"],
                "page": page_label,
                "chunk_index": meta["chunk_index"],
                "text": item["text"],
            }
        )

    context = "\n\n".join(context_parts)

    try:
        answer = await llm_service.generate(question, context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    return ChatResponse(answer=answer, sources=sources)
