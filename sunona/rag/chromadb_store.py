"""
Sunona Voice AI - ChromaDB Vector Store

Local vector store implementation using ChromaDB.
Ideal for development and small-scale deployments.

Features:
- Persistent local storage
- Built-in embedding functions
- Metadata filtering
- Collection management
"""

import os
import logging
from typing import Any, Dict, List, Optional

from sunona.rag.base_vectorstore import BaseVectorStore, Document, SearchResult
from sunona.rag.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class ChromaDBStore(BaseVectorStore):
    """
    ChromaDB vector store for local RAG.
    
    Uses ChromaDB for persistent vector storage with support for
    metadata filtering and semantic search.
    
    Example:
        ```python
        store = ChromaDBStore(
            collection_name="knowledge_base",
            persist_directory="./chroma_db"
        )
        
        async with store:
            await store.add_documents([Document(content="Hello")])
            results = await store.search("greeting")
        ```
    """
    
    def __init__(
        self,
        collection_name: str = "default",
        persist_directory: Optional[str] = None,
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-3-small",
        **kwargs
    ):
        """
        Initialize ChromaDB store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistent storage
            embedding_provider: Embedding provider to use
            embedding_model: Embedding model name
        """
        super().__init__(collection_name, **kwargs)
        
        self.persist_directory = persist_directory or "./.chroma_db"
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        
        self._client = None
        self._collection = None
        self._embedder: Optional[EmbeddingGenerator] = None
    
    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        if self._initialized:
            return
        
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "chromadb is required. Install with: pip install chromadb"
            )
        
        # Create client with persistence
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        )
        
        self._client = chromadb.Client(settings)
        
        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedder
        self._embedder = EmbeddingGenerator(
            provider=self.embedding_provider,
            model=self.embedding_model
        )
        
        self._initialized = True
        logger.info(f"ChromaDB initialized: {self.collection_name}")
    
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """Add documents to the collection."""
        if not self._initialized:
            await self.initialize()
        
        if not documents:
            return []
        
        # Generate embeddings if not provided
        if embeddings is None:
            contents = [doc.content for doc in documents]
            embeddings = await self._embedder.embed_batch(contents)
        
        # Prepare for ChromaDB
        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Add to collection
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
        
        logger.debug(f"Added {len(documents)} documents to {self.collection_name}")
        return ids
    
    async def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None
    ) -> List[SearchResult]:
        """Perform similarity search."""
        if not self._initialized:
            await self.initialize()
        
        # Generate query embedding if not provided
        if query_embedding is None:
            query_embedding = await self._embedder.embed(query)
        
        # Build query
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": k,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if filter:
            query_params["where"] = filter
        
        # Execute query
        results = self._collection.query(**query_params)
        
        # Convert to SearchResult objects
        search_results = []
        
        if results["ids"] and results["ids"][0]:
            for i, id in enumerate(results["ids"][0]):
                doc = Document(
                    id=id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {}
                )
                
                distance = results["distances"][0][i] if results["distances"] else 0
                # Convert distance to similarity score (for cosine)
                score = 1 - distance
                
                search_results.append(SearchResult(
                    document=doc,
                    score=score,
                    distance=distance
                ))
        
        return search_results
    
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete documents from the collection."""
        if not self._initialized:
            await self.initialize()
        
        if ids:
            self._collection.delete(ids=ids)
            return len(ids)
        elif filter:
            # Get matching IDs first
            results = self._collection.get(where=filter)
            if results["ids"]:
                self._collection.delete(ids=results["ids"])
                return len(results["ids"])
        
        return 0
    
    async def get(self, ids: List[str]) -> List[Document]:
        """Get documents by ID."""
        if not self._initialized:
            await self.initialize()
        
        results = self._collection.get(
            ids=ids,
            include=["documents", "metadatas"]
        )
        
        documents = []
        if results["ids"]:
            for i, id in enumerate(results["ids"]):
                doc = Document(
                    id=id,
                    content=results["documents"][i] if results["documents"] else "",
                    metadata=results["metadatas"][i] if results["metadatas"] else {}
                )
                documents.append(doc)
        
        return documents
    
    async def count(self) -> int:
        """Get the number of documents."""
        if not self._initialized:
            await self.initialize()
        return self._collection.count()
    
    async def clear(self) -> None:
        """Remove all documents."""
        if not self._initialized:
            await self.initialize()
        
        # Delete and recreate collection
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def close(self) -> None:
        """Close connections."""
        if self._embedder:
            await self._embedder.close()
        self._initialized = False
