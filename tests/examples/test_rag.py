"""
Sunona Voice AI - RAG Example

Demonstrates the Knowledge Base for context-aware conversations.

Usage:
    python examples/test_rag.py
    
Prerequisites:
    - pip install chromadb
    - OPENAI_API_KEY environment variable
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sunona.rag import KnowledgeBase


# Sample knowledge base content
COMPANY_KNOWLEDGE = """
# Sunona AI Company Information

## About Us
Sunona AI is a voice AI platform that enables developers to build 
intelligent voice assistants. Founded in 2024, we specialize in 
real-time voice conversation technology.

## Products
- Voice Assistant SDK: Build custom voice assistants
- Telephony Integration: Connect with Twilio, Plivo
- RAG Support: Knowledge-based conversations

## Pricing
- Free tier: 100 minutes/month
- Pro tier: $49/month for 1000 minutes
- Enterprise: Custom pricing

## Support
- Email: support@sunona.ai
- Hours: 9 AM - 6 PM EST, Monday-Friday
- SLA: 24-hour response for Pro, 4-hour for Enterprise

## Return Policy
We offer a 30-day money-back guarantee for all paid plans.
No questions asked. Contact billing@sunona.ai to process.
"""


async def main():
    print("=" * 60)
    print("Sunona AI - RAG (Knowledge Base) Example")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not set. Using mock mode.")
        print("Set the environment variable to use real embeddings.\n")
        return
    
    # Create knowledge base
    print("\n📚 Initializing Knowledge Base...")
    
    async with KnowledgeBase(
        collection_name="sunona_docs",
        store_type="chromadb",
    ) as kb:
        # Add content
        print("📝 Adding company knowledge...")
        doc_ids = await kb.add_text(
            COMPANY_KNOWLEDGE,
            metadata={"source": "company_handbook"},
        )
        print(f"   Added {len(doc_ids)} document chunks")
        
        # Get document count
        count = await kb.count()
        print(f"   Total documents in knowledge base: {count}")
        
        # Test queries
        queries = [
            "What is your return policy?",
            "How much does the Pro tier cost?",
            "What are your support hours?",
            "Tell me about Sunona AI products",
        ]
        
        print("\n" + "=" * 60)
        print("🔍 Testing Knowledge Retrieval")
        print("=" * 60)
        
        for query in queries:
            print(f"\n📌 Query: \"{query}\"")
            print("-" * 50)
            
            # Get context
            context = await kb.get_context(query, k=2)
            
            if context:
                # Truncate for display
                display_context = context[:300] + "..." if len(context) > 300 else context
                print(f"📄 Retrieved Context:\n{display_context}")
            else:
                print("❌ No relevant context found")
        
        # Clean up
        print("\n🧹 Cleaning up...")
        await kb.clear()
        print("✅ Knowledge base cleared")
    
    print("\n" + "=" * 60)
    print("RAG Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
