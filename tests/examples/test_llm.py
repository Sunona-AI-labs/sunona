"""Test script to debug LLM responses."""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sunona.llms import create_llm


async def test():
    print("Creating LLM...")
    llm = create_llm(
        provider="openrouter",
        model="mistralai/mistral-7b-instruct:free"
    )
    
    llm.set_system_prompt("You are a helpful assistant.")
    
    print("Sending message: 'hello'")
    print("Response chunks:")
    
    count = 0
    async for chunk in llm.chat_stream("hello"):
        count += 1
        print(f"  Chunk {count}: {repr(chunk)}")
    
    print(f"\nTotal chunks received: {count}")
    
    await llm.close()


if __name__ == "__main__":
    asyncio.run(test())
