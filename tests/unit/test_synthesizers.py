"""
Unit tests for Synthesizers.
"""

import pytest
import asyncio
import json
import base64
from unittest.mock import AsyncMock, patch
from sunona.synthesizer.elevenlabs_synthesizer import ElevenLabsSynthesizer

@pytest.mark.asyncio
async def test_elevenlabs_synthesizer_initialization():
    """Test standard initialization."""
    synthesizer = ElevenLabsSynthesizer(api_key="test-key", voice="Bella")
    assert synthesizer.api_key == "test-key"
    assert synthesizer.voice == "Bella"
    assert synthesizer.voice_id == "EXAVITQu4vr4xnSDxMaL"

@pytest.mark.asyncio
async def test_elevenlabs_format_mapping():
    """Test mapping of sample rates to ElevenLabs format strings."""
    synthesizer = ElevenLabsSynthesizer(api_key="test-key", sample_rate=44100, audio_format="pcm")
    assert synthesizer._get_output_format() == "pcm_44100"
    
    synthesizer = ElevenLabsSynthesizer(api_key="test-key", audio_format="mp3")
    assert synthesizer._get_output_format() == "mp3_44100_128"

@pytest.mark.asyncio
async def test_elevenlabs_connect_disconnect(mock_websocket):
    """Test connection lifecycle."""
    with patch("websockets.connect", return_value=mock_websocket):
        synthesizer = ElevenLabsSynthesizer(api_key="test-key")
        await synthesizer.connect()
        assert synthesizer._is_connected is True
        
        # Verify initial config message sent
        mock_websocket.send.assert_called()
        args, _ = mock_websocket.send.call_args
        sent_data = json.loads(args[0])
        assert "voice_settings" in sent_data
        
        await synthesizer.disconnect()
        assert synthesizer._is_connected is False

@pytest.mark.asyncio
async def test_elevenlabs_rest_synthesis(mock_http_client):
    """Test REST-based synthesis (non-streaming)."""
    # mock_http_client is already patched in conftest.py
    synthesizer = ElevenLabsSynthesizer(api_key="test-key")
    
    # Mock successful response
    mock_http_client.post.return_value.content = b"audio_content"
    mock_http_client.post.return_value.status_code = 200
    
    audio = await synthesizer.synthesize("Hello world")
    assert audio == b"audio_content"
    mock_http_client.post.assert_called()

@pytest.mark.asyncio
async def test_elevenlabs_receive_loop(mock_websocket):
    """Test handling of received audio chunks over WebSocket."""
    with patch("websockets.connect", return_value=mock_websocket):
        synthesizer = ElevenLabsSynthesizer(api_key="test-key")
        await synthesizer.connect()
        
        # Simulate receiving an audio chunk
        audio_data = b"fake-audio"
        audio_b64 = base64.b64encode(audio_data).decode()
        
        # We need to simulate messages received by the loop
        mock_websocket.recv.side_effect = [
            json.dumps({"audio": audio_b64, "isFinal": False}),
            json.dumps({"audio": "", "isFinal": True})
        ]
        
        # Wait a bit for the receive loop to process
        await asyncio.sleep(0.1)
        
        # Check if items are in the queue
        result1 = await synthesizer._audio_queue.get()
        assert result1 == audio_data
        
        result2 = await synthesizer._audio_queue.get()
        assert result2 is None
        
        await synthesizer.disconnect()
