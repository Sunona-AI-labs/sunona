"""
Integration tests requiring API keys.
Run with: pytest tests/integration/test_api_integrations.py -m requires_api
"""

import pytest
import asyncio
import os
from sunona.llms.openrouter_llm import OpenRouterLLM
from sunona.transcriber.deepgram_transcriber import DeepgramTranscriber
from sunona.synthesizer.elevenlabs_synthesizer import ElevenLabsSynthesizer

@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_llm_real_api():
    """Test OpenRouter with a real API call."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "test-key":
        pytest.skip("OPENROUTER_API_KEY not set")
    
    async with OpenRouterLLM(api_key=api_key) as llm:
        messages = [{"role": "user", "content": "Say 'ready'"}]
        response = await llm.generate(messages)
        assert "ready" in response.lower()

@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_transcriber_real_api(sample_audio_bytes):
    """Test Deepgram with a real API call."""
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key or api_key == "test-key":
        pytest.skip("DEEPGRAM_API_KEY not set")
        
    transcriber = DeepgramTranscriber(api_key=api_key)
    await transcriber.connect()
    
    try:
        # Send sample audio
        await transcriber.transcribe(sample_audio_bytes)
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Check if we got anything (might be empty for silent sample but should stay connected)
        assert transcriber._is_connected is True
    finally:
        await transcriber.disconnect()

@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_synthesizer_real_api():
    """Test ElevenLabs with a real API call."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "test-key":
        pytest.skip("ELEVENLABS_API_KEY not set")
        
    synthesizer = ElevenLabsSynthesizer(api_key=api_key)
    audio = await synthesizer.synthesize("Integration test.")
    
    assert len(audio) > 0
    assert audio.startswith(b'\xff\xfb') or audio.startswith(b'RIFF') # mp3 or wav
