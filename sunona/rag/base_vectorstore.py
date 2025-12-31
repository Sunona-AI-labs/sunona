"""
Sunona Voice AI - Base Vector Store

Abstract base class for vector store implementations.
Provides common interface for document storage and semantic search.

Features:
- Document model with metadata
- CRUD operations for documents
- Semantic similarity search
- Batch operations for efficiency
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """
    Document for vector store.
    
    Attributes:
        content: Document text content
        metadata: Additional metadata (title, source, etc.)
        id: Unique document identifier
        embedding: Pre-computed embedding (optional)
    """
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.id is None:
            import hashlib
            content_hash = hashlib.md5(self.content.encode()).hexdigest()[:12]
            self.id = f"doc_{content_hash}"
        
        # Add timestamp if not present
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            content=data["content"],
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


@dataclass
class SearchResult:
    """
    Result from similarity search.
    
    Attributes:
        document: The matched document
        score: Similarity score (higher is better)
        distance: Optional distance metric
    """
    document: Document
    score: float
    distance: Optional[float] = None


class BaseVectorStore(ABC):
    """
    Abstract base class for vector stores.
    
    Subclasses must implement:
    - add_documents(): Add documents to the store
    - search(): Perform similarity search
    - delete(): Remove documents
    - get(): Retrieve documents by ID
    
    Example:
        ```python
        store = ChromaDBStore(collection_name="my_docs")
        
        # Add documents
        docs = [Document(content="Hello world")]
        await store.add_documents(docs)
        
        # Search
        results = await store.search("greeting", k=5)
        ```
    """
    
    def __init__(self, collection_name: str = "default", **kwargs):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the collection/index
            **kwargs: Store-specific configuration
        """
        self.collection_name = collection_name
        self.config = kwargs
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store connection."""
        pass
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None
    ) -> List[SearchResult]:
        """
        Perform similarity search.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter: Metadata filter (optional)
            query_embedding: Pre-computed query embedding (optional)
            
        Returns:
            List of search results ordered by relevance
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Delete documents from the store.
        
        Args:
            ids: Document IDs to delete
            filter: Metadata filter for deletion
            
        Returns:
            Number of documents deleted
        """
        pass
    
    @abstractmethod
    async def get(
        self,
        ids: List[str]
    ) -> List[Document]:
        """
        Get documents by ID.
        
        Args:
            ids: Document IDs to retrieve
            
        Returns:
            List of documents
        """
        pass
    
    async def update_document(
        self,
        id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """
        Update a document.
        
        Default implementation deletes and re-adds. Override for efficiency.
        
        Args:
            id: Document ID
            content: New content (optional)
            metadata: New metadata (optional)
            embedding: New embedding (optional)
            
        Returns:
            True if updated successfully
        """
        existing = await self.get([id])
        if not existing:
            return False
        
        doc = existing[0]
        
        if content is not None:
            doc.content = content
        if metadata is not None:
            doc.metadata.update(metadata)
        if embedding is not None:
            doc.embedding = embedding
        
        await self.delete(ids=[id])
        await self.add_documents([doc], embeddings=[embedding] if embedding else None)
        
        return True
    
    async def count(self) -> int:
        """Get the number of documents in the store."""
        raise NotImplementedError("count() not implemented for this store")
    
    async def clear(self) -> None:
        """Remove all documents from the store."""
        raise NotImplementedError("clear() not implemented for this store")
    
    async def close(self) -> None:
        """Close the vector store connection."""
        pass
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
