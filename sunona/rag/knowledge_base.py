"""
Sunona Voice AI - Knowledge Base

High-level knowledge management for RAG pipelines.
Simplifies document ingestion, search, and context generation.

Features:
- Document ingestion from text, files, URLs
- Automatic chunking with overlap
- Context generation for LLM prompts
- Multiple vector store backends
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from sunona.rag.base_vectorstore import BaseVectorStore, Document, SearchResult
from sunona.rag.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """Configuration for text chunking."""
    chunk_size: int = 500
    chunk_overlap: int = 50
    separator: str = "\n\n"


class KnowledgeBase:
    """
    High-level knowledge management for RAG.
    
    Provides simple interface for:
    - Adding documents from text or files
    - Searching for relevant context
    - Generating context strings for LLM prompts
    
    Example:
        ```python
        kb = KnowledgeBase(collection_name="support_docs")
        
        async with kb:
            # Add documents
            await kb.add_text("Our return policy is 30 days.")
            await kb.add_file("docs/faq.txt")
            
            # Search
            context = await kb.get_context("return policy", k=3)
            
            # Use in prompt
            prompt = f"Based on this context:\n{context}\n\nAnswer: ..."
        ```
    """
    
    def __init__(
        self,
        collection_name: str = "knowledge",
        store_type: str = "chromadb",
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-3-small",
        chunk_config: Optional[ChunkConfig] = None,
        **kwargs
    ):
        """
        Initialize the knowledge base.
        
        Args:
            collection_name: Name of the vector store collection
            store_type: Vector store type ('chromadb', 'pinecone')
            embedding_provider: Embedding provider
            embedding_model: Embedding model
            chunk_config: Text chunking configuration
        """
        self.collection_name = collection_name
        self.store_type = store_type
        self.chunk_config = chunk_config or ChunkConfig()
        self.config = kwargs
        
        self._store: Optional[BaseVectorStore] = None
        self._embedder: Optional[EmbeddingGenerator] = None
        self._embedding_provider = embedding_provider
        self._embedding_model = embedding_model
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the knowledge base."""
        if self._initialized:
            return
        
        # Create vector store
        from sunona.rag import create_vectorstore
        
        self._store = create_vectorstore(
            store_type=self.store_type,
            collection_name=self.collection_name,
            embedding_provider=self._embedding_provider,
            embedding_model=self._embedding_model,
            **self.config
        )
        
        await self._store.initialize()
        
        # Create embedder for queries
        self._embedder = EmbeddingGenerator(
            provider=self._embedding_provider,
            model=self._embedding_model
        )
        
        self._initialized = True
        logger.info(f"Knowledge base initialized: {self.collection_name}")
    
    def _chunk_text(self, text: str, source: str = "text") -> List[Document]:
        """Split text into chunks with overlap."""
        chunks = []
        
        # Split by separator first
        paragraphs = text.split(self.chunk_config.separator)
        
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(para) > self.chunk_config.chunk_size:
                if current_chunk:
                    chunks.append(Document(
                        content=current_chunk.strip(),
                        metadata={
                            "source": source,
                            "chunk_index": chunk_index
                        }
                    ))
                    chunk_index += 1
                    
                    # Keep overlap from previous chunk
                    overlap_chars = self.chunk_config.chunk_overlap
                    if len(current_chunk) > overlap_chars:
                        current_chunk = current_chunk[-overlap_chars:]
                    else:
                        current_chunk = ""
                
                current_chunk = current_chunk + " " + para if current_chunk else para
            else:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(Document(
                content=current_chunk.strip(),
                metadata={
                    "source": source,
                    "chunk_index": chunk_index
                }
            ))
        
        return chunks
    
    async def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "text"
    ) -> List[str]:
        """
        Add text content to the knowledge base.
        
        Args:
            text: Text content to add
            metadata: Additional metadata
            source: Source identifier
            
        Returns:
            List of document IDs
        """
        if not self._initialized:
            await self.initialize()
        
        # Chunk the text
        documents = self._chunk_text(text, source)
        
        # Add metadata
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        
        # Add to store
        return await self._store.add_documents(documents)
    
    async def add_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add a text file to the knowledge base.
        
        Args:
            file_path: Path to the file
            metadata: Additional metadata
            
        Returns:
            List of document IDs
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        source = os.path.basename(file_path)
        file_metadata = {"file_path": file_path}
        if metadata:
            file_metadata.update(metadata)
        
        return await self.add_text(content, file_metadata, source)
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add pre-created documents."""
        if not self._initialized:
            await self.initialize()
        return await self._store.add_documents(documents)
    
    async def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter
            
        Returns:
            List of search results
        """
        if not self._initialized:
            await self.initialize()
        
        return await self._store.search(query, k, filter)
    
    async def get_context(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        separator: str = "\n\n---\n\n"
    ) -> str:
        """
        Get context string for LLM prompts.
        
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter
            separator: Separator between chunks
            
        Returns:
            Concatenated context string
        """
        results = await self.search(query, k, filter)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            context_parts.append(result.document.content)
        
        return separator.join(context_parts)
    
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete documents."""
        if not self._initialized:
            await self.initialize()
        return await self._store.delete(ids, filter)
    
    async def count(self) -> int:
        """Get document count."""
        if not self._initialized:
            await self.initialize()
        return await self._store.count()
    
    async def clear(self) -> None:
        """Clear all documents."""
        if not self._initialized:
            await self.initialize()
        await self._store.clear()
    
    async def close(self) -> None:
        """Close the knowledge base."""
        if self._store:
            await self._store.close()
        if self._embedder:
            await self._embedder.close()
        self._initialized = False
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
