"""
Sunona Voice AI - Knowledge Base API Routes
REST API for managing RAG knowledge bases and documents.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel, Field

from sunona.api.auth import get_api_key, APIKey

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


class KnowledgeBaseType(str, Enum):
    DOCUMENTS = "documents"
    FAQ = "faq"
    WEBSITE = "website"
    API = "api"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class CreateKnowledgeBaseRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    kb_type: KnowledgeBaseType = KnowledgeBaseType.DOCUMENTS
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class KnowledgeBaseResponse(BaseModel):
    kb_id: str
    name: str
    description: str
    kb_type: str
    status: str
    document_count: int
    total_chunks: int
    embedding_model: str
    account_id: str
    created_at: str
    updated_at: str


class DocumentResponse(BaseModel):
    doc_id: str
    kb_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: str


# In-memory storage
_knowledge_bases: Dict[str, Dict] = {}
_documents: Dict[str, List[Dict]] = {}
_kb_counter = 0
_doc_counter = 0


@router.get("")
async def list_knowledge_bases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    api_key: APIKey = Depends(get_api_key),
) -> Dict[str, Any]:
    kbs = [kb for kb in _knowledge_bases.values() if kb["account_id"] == api_key.account_id]
    total = len(kbs)
    start = (page - 1) * page_size
    return {"knowledge_bases": kbs[start:start+page_size], "total": total, "page": page}


@router.post("", status_code=201)
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequest,
    api_key: APIKey = Depends(get_api_key),
) -> KnowledgeBaseResponse:
    global _kb_counter
    _kb_counter += 1
    kb_id = f"kb_{_kb_counter:06d}"
    now = datetime.now().isoformat()
    
    kb = {
        "kb_id": kb_id,
        "name": request.name,
        "description": request.description,
        "kb_type": request.kb_type.value,
        "status": "ready",
        "document_count": 0,
        "total_chunks": 0,
        "embedding_model": request.embedding_model,
        "chunk_size": request.chunk_size,
        "chunk_overlap": request.chunk_overlap,
        "account_id": api_key.account_id,
        "created_at": now,
        "updated_at": now,
    }
    _knowledge_bases[kb_id] = kb
    _documents[kb_id] = []
    return KnowledgeBaseResponse(**kb)


@router.get("/{kb_id}")
async def get_knowledge_base(kb_id: str, api_key: APIKey = Depends(get_api_key)):
    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb


@router.put("/{kb_id}")
async def update_knowledge_base(
    kb_id: str,
    request: CreateKnowledgeBaseRequest,
    api_key: APIKey = Depends(get_api_key),
):
    kb = _knowledge_bases.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    kb["name"] = request.name
    kb["description"] = request.description
    kb["updated_at"] = datetime.now().isoformat()
    return kb


@router.delete("/{kb_id}", status_code=204)
async def delete_knowledge_base(kb_id: str, api_key: APIKey = Depends(get_api_key)):
    if kb_id in _knowledge_bases:
        del _knowledge_bases[kb_id]
        if kb_id in _documents:
            del _documents[kb_id]


# Document management
@router.get("/{kb_id}/documents")
async def list_documents(kb_id: str, api_key: APIKey = Depends(get_api_key)):
    if kb_id not in _knowledge_bases:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"documents": _documents.get(kb_id, []), "total": len(_documents.get(kb_id, []))}


@router.post("/{kb_id}/documents", status_code=201)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    api_key: APIKey = Depends(get_api_key),
):
    global _doc_counter
    if kb_id not in _knowledge_bases:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    _doc_counter += 1
    doc_id = f"doc_{_doc_counter:06d}"
    now = datetime.now().isoformat()
    
    doc = {
        "doc_id": doc_id,
        "kb_id": kb_id,
        "filename": file.filename,
        "file_type": file.content_type or "unknown",
        "file_size": 0,
        "status": "processing",
        "chunk_count": 0,
        "created_at": now,
    }
    _documents[kb_id].append(doc)
    _knowledge_bases[kb_id]["document_count"] += 1
    
    # Simulate processing completion
    doc["status"] = "ready"
    doc["chunk_count"] = 25
    _knowledge_bases[kb_id]["total_chunks"] += 25
    
    return doc


@router.delete("/{kb_id}/documents/{doc_id}", status_code=204)
async def delete_document(kb_id: str, doc_id: str, api_key: APIKey = Depends(get_api_key)):
    if kb_id not in _documents:
        return
    docs = _documents[kb_id]
    _documents[kb_id] = [d for d in docs if d["doc_id"] != doc_id]


# Search
@router.post("/{kb_id}/search")
async def search_knowledge_base(
    kb_id: str,
    query: str,
    top_k: int = Query(5, ge=1, le=20),
    api_key: APIKey = Depends(get_api_key),
):
    if kb_id not in _knowledge_bases:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Demo search results
    return {
        "query": query,
        "results": [
            {"chunk_id": f"chunk_{i}", "content": f"Sample content matching '{query}'...", "score": 0.9 - i*0.1}
            for i in range(min(top_k, 5))
        ],
        "total_results": min(top_k, 5),
    }


# Assign to agent
@router.post("/{kb_id}/assign")
async def assign_to_agent(
    kb_id: str,
    agent_id: str,
    api_key: APIKey = Depends(get_api_key),
):
    if kb_id not in _knowledge_bases:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"kb_id": kb_id, "agent_id": agent_id, "status": "assigned"}
