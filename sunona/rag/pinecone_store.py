"""
Sunona Voice AI - Pinecone Vector Store

Pinecone integration for production-scale RAG.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False


@dataclass
class PineconeDocument:
    """Document for Pinecone storage."""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]


class PineconeStore:
    """
    Pinecone vector store for enterprise-scale RAG.
    
    Features:
        - Serverless scaling
        - Metadata filtering
        - Hybrid search
        - Namespace isolation
    
    Example:
        ```python
        store = PineconeStore(index_name="knowledge-base")
        await store.upsert([doc1, doc2])
        results = await store.search(query_embedding, top_k=5)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: str = "sunona-kb",
        dimension: int = 1536,
        metric: str = "cosine",
        namespace: str = "default",
    ):
        if not PINECONE_AVAILABLE:
            raise ImportError("pinecone-client required: pip install pinecone-client")
        
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY required")
        
        self._client = Pinecone(api_key=self.api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.namespace = namespace
        
        # Get or create index
        if index_name not in self._client.list_indexes().names():
            self._client.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        
        self._index = self._client.Index(index_name)
        logger.info(f"Pinecone store initialized: {index_name}")
    
    async def upsert(self, documents: List[PineconeDocument]) -> int:
        """Upsert documents."""
        vectors = [
            {
                "id": doc.id,
                "values": doc.embedding,
                "metadata": {**doc.metadata, "content": doc.content[:1000]},
            }
            for doc in documents
        ]
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._index.upsert(vectors=vectors, namespace=self.namespace)
        )
        
        return result.upserted_count
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            lambda: self._index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter,
                namespace=self.namespace,
                include_metadata=True,
            )
        )
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "content": match.metadata.get("content", ""),
                "metadata": match.metadata,
            }
            for match in result.matches
        ]
    
    async def delete(self, ids: List[str]) -> bool:
        """Delete documents by ID."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._index.delete(ids=ids, namespace=self.namespace)
        )
        return True
