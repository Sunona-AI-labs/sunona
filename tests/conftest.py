"""
Sunona Voice AI - Test Configuration

This module provides shared fixtures and configuration for all tests.
Uses pytest-asyncio for async test support.
"""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Async Event Loop Configuration
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    test_env = {
        "OPENROUTER_API_KEY": "test-openrouter-key",
        "OPENROUTER_MODEL": "mistralai/mistral-7b-instruct:free",
        "GROQ_API_KEY": "test-groq-key",
        "DEEPGRAM_API_KEY": "test-deepgram-key",
        "ELEVENLABS_API_KEY": "test-elevenlabs-key",
        "ELEVENLABS_VOICE_ID": "test-voice-id",
        "TWILIO_ACCOUNT_SID": "ACtest123",
        "TWILIO_AUTH_TOKEN": "test-auth-token",
        "TWILIO_PHONE_NUMBER": "+15551234567",
        "REDIS_URL": "",  # Disable Redis in tests
        "SUNONA_DEBUG": "true",
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


# =============================================================================
# Mock Fixtures for External Services
# =============================================================================

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for external API calls."""
    with patch("aiohttp.ClientSession") as mock:
        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        
        # Mock successful response
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value={"success": True})
        response.text = AsyncMock(return_value="OK")
        response.read = AsyncMock(return_value=b"audio_data")
        
        session.post = AsyncMock(return_value=response)
        session.get = AsyncMock(return_value=response)
        session.ws_connect = AsyncMock()
        
        mock.return_value = session
        yield session


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock(return_value='{"type": "test"}')
    ws.close = AsyncMock()
    ws.__aiter__ = AsyncMock(return_value=iter([]))
    return ws


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing without Redis server."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.keys = AsyncMock(return_value=[])
    redis.ping = AsyncMock(return_value=True)
    return redis


# =============================================================================
# LLM Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_response():
    """Standard mock LLM response."""
    return {
        "id": "test-completion-id",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the LLM."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def mock_streaming_llm_response():
    """Mock streaming LLM response chunks."""
    chunks = [
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " there"}}]},
        {"choices": [{"delta": {"content": "!"}}]},
        {"choices": [{"delta": {}}]},  # End of stream
    ]
    return chunks


# =============================================================================
# Audio Fixtures
# =============================================================================

@pytest.fixture
def sample_audio_bytes() -> bytes:
    """Sample audio bytes for testing (silent WAV header)."""
    # Minimal valid WAV file (44 bytes header + 0 data)
    return (
        b'RIFF'      # ChunkID
        b'\x24\x00\x00\x00'  # ChunkSize (36 bytes)
        b'WAVE'      # Format
        b'fmt '      # Subchunk1ID
        b'\x10\x00\x00\x00'  # Subchunk1Size (16 for PCM)
        b'\x01\x00'  # AudioFormat (1 = PCM)
        b'\x01\x00'  # NumChannels (1 = mono)
        b'\x80\x3e\x00\x00'  # SampleRate (16000)
        b'\x00\x7d\x00\x00'  # ByteRate (32000)
        b'\x02\x00'  # BlockAlign (2)
        b'\x10\x00'  # BitsPerSample (16)
        b'data'      # Subchunk2ID
        b'\x00\x00\x00\x00'  # Subchunk2Size (0 bytes of data)
    )


@pytest.fixture
def sample_transcription():
    """Sample transcription result."""
    return {
        "text": "Hello, this is a test transcription.",
        "confidence": 0.95,
        "words": [
            {"word": "Hello", "start": 0.0, "end": 0.5},
            {"word": "this", "start": 0.6, "end": 0.8},
            {"word": "is", "start": 0.9, "end": 1.0},
            {"word": "a", "start": 1.1, "end": 1.2},
            {"word": "test", "start": 1.3, "end": 1.5},
            {"word": "transcription", "start": 1.6, "end": 2.2},
        ]
    }


# =============================================================================
# Agent Fixtures
# =============================================================================

@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing."""
    return {
        "agent_name": "Test Agent",
        "agent_type": "contextual",
        "agent_welcome_message": "Hello! How can I help you today?",
        "tasks": [
            {
                "task_type": "conversation",
                "task_config": {
                    "system_prompt": "You are a helpful assistant."
                }
            }
        ],
        "llm_config": {
            "provider": "openrouter",
            "model": "mistralai/mistral-7b-instruct:free",
            "temperature": 0.7
        },
        "transcriber_config": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en"
        },
        "synthesizer_config": {
            "provider": "edge",
            "voice": "en-US-JennyNeural"
        }
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for context testing."""
    return [
        {"role": "user", "content": "Hi there!"},
        {"role": "assistant", "content": "Hello! How can I help you today?"},
        {"role": "user", "content": "What's the weather like?"},
    ]


# =============================================================================
# FastAPI Test Client Fixture
# =============================================================================

@pytest.fixture
async def test_client():
    """Create async test client for FastAPI server."""
    from httpx import AsyncClient, ASGITransport
    
    # Import here to avoid circular imports
    from sunona.server import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# =============================================================================
# Utility Functions
# =============================================================================

def assert_valid_response(response: dict, required_keys: list[str]) -> None:
    """Assert that response contains all required keys."""
    for key in required_keys:
        assert key in response, f"Missing required key: {key}"


async def async_iter(items):
    """Helper to create async iterator from list."""
    for item in items:
        yield item
