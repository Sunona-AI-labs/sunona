"""
Unit tests for Transcribers.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sunona.transcriber.deepgram_transcriber import DeepgramTranscriber

@pytest.mark.asyncio
async def test_deepgram_transcriber_initialization():
    """Test standard initialization."""
    transcriber = DeepgramTranscriber(api_key="test-key")
    assert transcriber.api_key == "test-key"
    assert transcriber.model == "nova-2"
    assert transcriber.language == "en"

@pytest.mark.asyncio
async def test_deepgram_transcriber_initialization_missing_key(monkeypatch):
    """Test initialization fails without API key."""
    monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Deepgram API key required"):
        DeepgramTranscriber()

@pytest.mark.asyncio
async def test_deepgram_url_building():
    """Test URL construction with parameters."""
    transcriber = DeepgramTranscriber(
        api_key="test-key", 
        model="custom-model", 
        language="fr",
        endpointing=300
    )
    url = transcriber._build_url()
    assert "model=custom-model" in url
    assert "language=fr" in url
    assert "endpointing=300" in url
    assert "api.deepgram.com" in url

@pytest.mark.asyncio
async def test_deepgram_connect_disconnect(mock_websocket):
    """Test connection lifecycle."""
    with patch("websockets.connect", return_value=mock_websocket):
        transcriber = DeepgramTranscriber(api_key="test-key")
        await transcriber.connect()
        assert transcriber._is_connected is True
        
        await transcriber.disconnect()
        assert transcriber._is_connected is False

@pytest.mark.asyncio
async def test_deepgram_parse_result():
    """Test parsing Deepgram JSON messages."""
    transcriber = DeepgramTranscriber(api_key="test-key")
    data = {
        "type": "Results",
        "channel": {
            "alternatives": [
                {"transcript": "Hello world", "confidence": 0.99, "words": []}
            ]
        },
        "is_final": True,
        "start": 0.0,
        "duration": 1.0
    }
    result = transcriber._parse_result(data)
    assert result["text"] == "Hello world"
    assert result["is_final"] is True
    assert result["confidence"] == 0.99

@pytest.mark.asyncio
async def test_deepgram_transcribe_chunk(mock_websocket):
    """Test sending a single chunk of audio."""
    with patch("websockets.connect", return_value=mock_websocket):
        transcriber = DeepgramTranscriber(api_key="test-key")
        await transcriber.connect()
        
        # Mock receiving a result
        mock_websocket.recv.return_value = '{"type": "Results", "channel": {"alternatives": [{"transcript": "Detected text"}]}}'
        
        # We need to manually trigger the receive loop processing or mock the queue
        # In this simple test, we just check if send was called
        await transcriber.transcribe(b"dummy audio")
        mock_websocket.send.assert_called()
        
        await transcriber.disconnect()
