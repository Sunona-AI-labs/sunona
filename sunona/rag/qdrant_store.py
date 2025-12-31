"""
Sunona Voice AI - Qdrant Vector Store

Qdrant integration for high-performance RAG.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class QdrantStore:
    """
    Qdrant vector store for high-performance RAG.
    
    Features:
        - Local or cloud deployment
        - Advanced filtering
        - Payload indexing
        - Batch operations
    
    Example:
        ```python
        store = QdrantStore(collection="knowledge")
        await store.add_documents(docs)
        results = await store.search(embedding, top_k=5)
        ```
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection: str = "sunona_knowledge",
        dimension: int = 1536,
        distance: str = "cosine",
    ):
        if not QDRANT_AVAILABLE:
            raise ImportError("qdrant-client required: pip install qdrant-client")
        
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection = collection
        self.dimension = dimension
        
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT,
        }
        self._distance = distance_map.get(distance, Distance.COSINE)
        
        # Connect
        if self.api_key:
            self._client = QdrantClient(url=self.url, api_key=self.api_key)
        else:
            self._client = QdrantClient(url=self.url)
        
        # Create collection if needed
        self._ensure_collection()
        
        logger.info(f"Qdrant store initialized: {collection}")
    
    def _ensure_collection(self):
        """Ensure collection exists."""
        collections = self._client.get_collections().collections
        exists = any(c.name == self.collection for c in collections)
        
        if not exists:
            self._client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=self._distance,
                ),
            )
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
    ) -> int:
        """Add documents with embeddings."""
        points = []
        for doc in documents:
            point = PointStruct(
                id=doc.get("id", str(uuid.uuid4())),
                vector=doc["embedding"],
                payload={
                    "content": doc.get("content", ""),
                    **doc.get("metadata", {}),
                },
            )
            points.append(point)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.upsert(
                collection_name=self.collection,
                points=points,
            )
        )
        
        return len(points)
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_conditions: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        # Build filter
        query_filter = None
        if filter_conditions:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter_conditions.items()
            ]
            query_filter = Filter(must=conditions)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self._client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
            )
        )
        
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "content": r.payload.get("content", ""),
                "metadata": r.payload,
            }
            for r in results
        ]
    
    async def delete(self, ids: List[str]) -> bool:
        """Delete documents."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.delete(
                collection_name=self.collection,
                points_selector={"points": ids},
            )
        )
        return True
