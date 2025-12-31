"""
Sunona Voice AI - Knowledge Base Agent

Agent powered by a knowledge base for accurate, grounded responses.
Uses RAG (Retrieval Augmented Generation) to answer questions.
"""

import logging
from typing import Any, Dict, List, Optional

from sunona.agents.base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentCapability, AgentState
)

logger = logging.getLogger(__name__)


class KnowledgeBaseAgent(BaseAgent):
    """
    Agent that answers questions using a knowledge base.
    
    Features:
    - RAG-powered responses
    - Grounded in actual business data
    - Cites sources
    - Falls back gracefully when knowledge lacking
    - Auto-transfers for unknown questions
    
    Best for:
    - Customer FAQ
    - Product information
    - Policy questions
    - Technical support
    
    Example:
        ```python
        # Build knowledge base from website/docs
        kb = await build_knowledge_from_website("https://acme.com")
        
        # Create agent
        agent = KnowledgeBaseAgent(
            knowledge_base=kb,
            llm=my_llm,
        )
        
        # Ask questions
        response = await agent.process_message("What are your business hours?")
        # Agent searches KB and provides accurate answer
        ```
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm: Optional[Any] = None,
        knowledge_base: Optional[Any] = None,
        vector_store: Optional[Any] = None,
    ):
        super().__init__(config, llm)
        
        self.knowledge_base = knowledge_base
        self.vector_store = vector_store
        
        # Retrieval settings
        self.top_k = 5  # Number of chunks to retrieve
        self.confidence_threshold = 0.5
        
        # Track unknown questions
        self._unknown_questions: List[str] = []
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        return [AgentCapability.KNOWLEDGE_BASE, AgentCapability.CONVERSATION]
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process message using knowledge base."""
        self._set_state(AgentState.LISTENING)
        self.add_message("user", message)
        
        # Retrieve relevant knowledge
        context = await self._retrieve_context(message)
        
        if not context:
            # No relevant knowledge found
            return await self._handle_no_context(message)
        
        # Generate response with context
        self._set_state(AgentState.THINKING)
        response = await self._generate_with_context(message, context)
        
        self.add_message("assistant", response)
        self._set_state(AgentState.SPEAKING)
        
        return AgentResponse(
            text=response,
            data={
                "sources": context.get("sources", []),
                "confidence": context.get("confidence", 0.7),
                "grounded": True,
            },
        )
    
    async def _retrieve_context(
        self,
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve relevant context from knowledge base."""
        
        # Try vector store first
        if self.vector_store:
            try:
                results = await self._search_vector_store(query)
                if results:
                    return results
            except Exception as e:
                logger.error(f"Vector search error: {e}")
        
        # Try direct knowledge base search
        if self.knowledge_base:
            try:
                results = self._search_knowledge_base(query)
                if results:
                    return results
            except Exception as e:
                logger.error(f"KB search error: {e}")
        
        return None
    
    async def _search_vector_store(
        self,
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """Search vector store for relevant content."""
        # This would integrate with ChromaDB, Pinecone, etc.
        # For now, return None (implement in production)
        return None
    
    def _search_knowledge_base(
        self,
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """Search knowledge base for relevant content."""
        if not self.knowledge_base:
            return None
        
        # Simple keyword search in full text
        query_words = set(query.lower().split())
        
        results = []
        
        # Search chunks
        if hasattr(self.knowledge_base, "chunks"):
            for chunk in self.knowledge_base.chunks:
                chunk_words = set(chunk.content.lower().split())
                overlap = len(query_words & chunk_words)
                
                if overlap >= 2:  # At least 2 word match
                    results.append({
                        "content": chunk.content[:500],
                        "source": chunk.source,
                        "score": overlap / len(query_words),
                    })
        
        # Search FAQ
        if hasattr(self.knowledge_base, "faq"):
            for qa in self.knowledge_base.faq:
                question = qa.get("question", "").lower()
                if any(word in question for word in query_words):
                    results.append({
                        "content": f"Q: {qa['question']}\nA: {qa['answer']}",
                        "source": "FAQ",
                        "score": 0.9,  # FAQ matches are high confidence
                    })
        
        if not results:
            return None
        
        # Sort by score and take top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        top_results = results[:self.top_k]
        
        # Calculate overall confidence
        avg_score = sum(r["score"] for r in top_results) / len(top_results)
        
        return {
            "context": "\n\n".join(r["content"] for r in top_results),
            "sources": [r["source"] for r in top_results],
            "confidence": avg_score,
        }
    
    async def _generate_with_context(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """Generate response using retrieved context."""
        if not self.llm:
            # Return context directly
            return context.get("context", "")[:300]
        
        prompt = f"""Use the following information to answer the question.
If the information doesn't contain the answer, say "I don't have that specific information, but I can connect you with someone who does."

INFORMATION:
{context.get('context', '')}

QUESTION: {question}

Provide a concise, conversational answer suitable for a phone call (1-3 sentences).
"""
        
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = await self.llm.generate(messages)
            
            # Check if response indicates lack of knowledge
            if any(phrase in response.lower() for phrase in [
                "don't have", "don't know", "can't find", "not sure"
            ]):
                self.record_unknown()
            else:
                self.reset_unknown_count()
            
            return response
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return context.get("context", "")[:300]
    
    async def _handle_no_context(self, message: str) -> AgentResponse:
        """Handle when no relevant context is found."""
        self._unknown_questions.append(message)
        self.record_unknown()
        
        if self.should_transfer_due_to_unknowns():
            return await self.transfer("no_knowledge")
        
        # Try to answer with LLM anyway
        if self.llm:
            response = await self.generate_response()
        else:
            response = "I don't have specific information about that. Would you like me to connect you with someone who can help?"
        
        self.add_message("assistant", response)
        
        return AgentResponse(
            text=response,
            data={
                "grounded": False,
                "confidence": 0.3,
            },
        )
    
    def add_knowledge(
        self,
        content: str,
        source: str = "manual",
        metadata: Optional[Dict] = None,
    ):
        """Add knowledge dynamically."""
        if hasattr(self.knowledge_base, "chunks"):
            from sunona.knowledge.knowledge_builder import KnowledgeChunk, SourceType
            
            chunk = KnowledgeChunk(
                content=content,
                source=source,
                source_type=SourceType.TEXT,
                metadata=metadata or {},
            )
            self.knowledge_base.chunks.append(chunk)
            logger.info(f"Added knowledge: {len(content)} chars from {source}")
    
    def get_unknown_questions(self) -> List[str]:
        """Get list of questions agent couldn't answer."""
        return self._unknown_questions
    
    def get_kb_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        stats = {
            "has_knowledge_base": self.knowledge_base is not None,
            "has_vector_store": self.vector_store is not None,
            "unknown_questions": len(self._unknown_questions),
        }
        
        if self.knowledge_base:
            if hasattr(self.knowledge_base, "chunks"):
                stats["chunk_count"] = len(self.knowledge_base.chunks)
            if hasattr(self.knowledge_base, "faq"):
                stats["faq_count"] = len(self.knowledge_base.faq)
        
        return stats
