"""
Sunona Voice AI - RAG Package

Retrieval-Augmented Generation for knowledge-based voice assistants.

Provides:
- KnowledgeBase: High-level knowledge management
- BaseVectorStore: Abstract vector store interface
- ChromaDBStore: Local vector store (development)
- Embeddings: Text embedding generation
"""

from sunona.rag.base_vectorstore import BaseVectorStore, Document
from sunona.rag.embeddings import EmbeddingGenerator
from sunona.rag.knowledge_base import KnowledgeBase

__all__ = [
    "BaseVectorStore",
    "Document",
    "EmbeddingGenerator", 
    "KnowledgeBase",
]


def create_vectorstore(store_type: str = "chromadb", **kwargs) -> BaseVectorStore:
    """
    Factory function to create a vector store.
    
    Args:
        store_type: Vector store type ('chromadb', 'pinecone')
        **kwargs: Store-specific configuration
        
    Returns:
        BaseVectorStore: A vector store instance
    """
    from sunona.rag.chromadb_store import ChromaDBStore
    
    stores = {
        "chromadb": ChromaDBStore,
        "chroma": ChromaDBStore,
    }
    
    if store_type not in stores:
        raise ValueError(
            f"Unknown vector store: '{store_type}'. "
            f"Available: {list(stores.keys())}"
        )
    
    return stores[store_type](**kwargs)
