"""
Sunona Voice AI - Embeddings Generator

Text embedding generation for RAG pipelines.
Supports OpenAI and sentence-transformers models.

Features:
- OpenAI text-embedding-3-small/large
- Local sentence-transformers models
- Batch processing for efficiency
- Caching for repeated queries
"""

import os
import logging
from typing import List, Optional, Dict, Any
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generate text embeddings for RAG.
    
    Supports multiple backends:
    - OpenAI: text-embedding-3-small, text-embedding-3-large
    - Local: sentence-transformers models
    
    Example:
        ```python
        generator = EmbeddingGenerator(provider="openai")
        
        # Single embedding
        embedding = await generator.embed("Hello world")
        
        # Batch embeddings
        embeddings = await generator.embed_batch(["Hello", "World"])
        ```
    """
    
    OPENAI_MODELS = {
        "text-embedding-3-small": {"dimensions": 1536},
        "text-embedding-3-large": {"dimensions": 3072},
        "text-embedding-ada-002": {"dimensions": 1536},
    }
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None,
        batch_size: int = 100,
        **kwargs
    ):
        """
        Initialize the embedding generator.
        
        Args:
            provider: Embedding provider ('openai', 'local')
            model: Model name/identifier
            api_key: API key (for OpenAI)
            dimensions: Output dimensions (optional)
            batch_size: Maximum batch size for processing
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.dimensions = dimensions
        self.batch_size = batch_size
        self.config = kwargs
        
        self._client = None
        self._local_model = None
        
        # Set dimensions from model if not specified
        if self.dimensions is None and model in self.OPENAI_MODELS:
            self.dimensions = self.OPENAI_MODELS[model]["dimensions"]
        
        logger.info(f"Embedding generator initialized: {provider}/{model}")
    
    async def _get_openai_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai is required. Install with: pip install openai")
        return self._client
    
    def _get_local_model(self):
        """Get or load local sentence-transformers model."""
        if self._local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._local_model = SentenceTransformer(self.model)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )
        return self._local_model
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embeddings = await self.embed_batch([text])
        return embeddings[0]
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.provider == "openai":
            return await self._embed_openai(texts)
        elif self.provider == "local":
            return await self._embed_local(texts)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        client = await self._get_openai_client()
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                response = await client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )
                
                # Sort by index to maintain order
                sorted_embeddings = sorted(
                    response.data, 
                    key=lambda x: x.index
                )
                
                batch_embeddings = [e.embedding for e in sorted_embeddings]
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"OpenAI embedding error: {e}")
                raise
        
        return all_embeddings
    
    async def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model."""
        model = self._get_local_model()
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(texts, convert_to_numpy=True).tolist()
        )
        
        return embeddings
    
    async def close(self) -> None:
        """Close any open connections."""
        if self._client:
            await self._client.close()
            self._client = None
    
    @property
    def embedding_dimensions(self) -> int:
        """Get the embedding dimensions."""
        return self.dimensions or 1536


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score (-1 to 1)
    """
    import math
    
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)
