"""
Sunona Voice AI - Unit Tests for Models

Tests for Pydantic models including validation, serialization,
and configuration parsing.
"""

import pytest
from pydantic import ValidationError


class TestEnums:
    """Tests for model enums."""
    
    def test_agent_type_values(self):
        """Test AgentType enum values."""
        from sunona.models import AgentType
        
        assert AgentType.CONTEXTUAL == "contextual"
        assert AgentType.EXTRACTION == "extraction"
        assert AgentType.GRAPH == "graph"
        assert AgentType.KNOWLEDGE_BASE == "knowledge_base"
        assert AgentType.WEBHOOK == "webhook"
        assert AgentType.SUMMARIZATION == "summarization"
    
    def test_task_type_values(self):
        """Test TaskType enum values."""
        from sunona.models import TaskType
        
        assert TaskType.CONVERSATION == "conversation"
        assert TaskType.EXTRACTION == "extraction"
        assert TaskType.SUMMARIZATION == "summarization"
    
    def test_flow_type_values(self):
        """Test FlowType enum values."""
        from sunona.models import FlowType
        
        assert FlowType.STREAMING == "streaming"
        assert FlowType.BATCH == "batch"
        assert FlowType.WEBSOCKET == "websocket"


class TestTranscriberConfig:
    """Tests for Transcriber configuration model."""
    
    def test_default_values(self):
        """Test Transcriber has correct defaults."""
        from sunona.models import Transcriber
        
        transcriber = Transcriber()
        
        assert transcriber.model == "nova-2"
        assert transcriber.provider == "deepgram"
        assert transcriber.stream is True
        assert transcriber.sampling_rate == 16000
        assert transcriber.encoding == "linear16"
    
    def test_custom_values(self):
        """Test Transcriber with custom values."""
        from sunona.models import Transcriber
        
        transcriber = Transcriber(
            provider="groq",
            model="whisper-large-v3",
            language="en-US"
        )
        
        assert transcriber.provider == "groq"
        assert transcriber.model == "whisper-large-v3"
        assert transcriber.language == "en-US"
    
    def test_valid_providers(self):
        """Test that valid providers are accepted."""
        from sunona.models import Transcriber
        
        valid_providers = ["deepgram", "groq", "sarvam", "assemblyai"]
        
        for provider in valid_providers:
            transcriber = Transcriber(provider=provider)
            assert transcriber.provider == provider


class TestSynthesizerConfig:
    """Tests for Synthesizer configuration model."""
    
    def test_default_values(self):
        """Test Synthesizer has correct defaults."""
        from sunona.models import Synthesizer
        
        synth = Synthesizer()
        
        assert synth.provider == "elevenlabs"
        assert synth.audio_format == "mp3"
        assert synth.sampling_rate == 16000
    
    def test_elevenlabs_config(self):
        """Test ElevenLabs synthesizer config."""
        from sunona.models import Synthesizer, ElevenLabsConfig
        
        synth = Synthesizer(
            provider="elevenlabs",
            provider_config=ElevenLabsConfig(
                voice="Sarah",
                voice_id="test-voice-id",
                model="eleven_turbo_v2_5"
            )
        )
        
        assert synth.provider == "elevenlabs"
        assert synth.provider_config.voice == "Sarah"
        assert synth.provider_config.model == "eleven_turbo_v2_5"
    
    def test_valid_providers(self):
        """Test that valid TTS providers are accepted."""
        from sunona.models import Synthesizer
        
        valid_providers = ["elevenlabs", "openai", "edge", "deepgram"]
        
        for provider in valid_providers:
            synth = Synthesizer(provider=provider)
            assert synth.provider == provider


class TestLLMConfig:
    """Tests for LLM configuration model."""
    
    def test_default_values(self):
        """Test LLMConfig has correct defaults."""
        from sunona.models import LLMConfig
        
        llm = LLMConfig()
        
        assert llm.max_tokens == 150
        assert llm.provider == "openrouter"
        assert llm.streaming is True
    
    def test_temperature_bounds(self):
        """Test that temperature is within valid bounds."""
        from sunona.models import LLMConfig
        
        # Valid temperatures
        llm_low = LLMConfig(temperature=0.0)
        llm_high = LLMConfig(temperature=2.0)
        
        assert llm_low.temperature == 0.0
        assert llm_high.temperature == 2.0
    
    def test_custom_model(self):
        """Test LLMConfig with custom model."""
        from sunona.models import LLMConfig
        
        llm = LLMConfig(
            provider="groq",
            model="llama-3.1-70b-versatile",
            max_tokens=500,
            temperature=0.5
        )
        
        assert llm.provider == "groq"
        assert llm.model == "llama-3.1-70b-versatile"
        assert llm.max_tokens == 500


class TestAgentConfig:
    """Tests for Agent configuration models."""
    
    def test_create_agent_request(self):
        """Test CreateAgentRequest model."""
        from sunona.models import CreateAgentRequest
        
        request = CreateAgentRequest(
            agent_name="Test Agent",
            agent_type="contextual"
        )
        
        assert request.agent_name == "Test Agent"
        assert request.agent_type == "contextual"
    
    def test_system_prompt_generation(self, sample_agent_config):
        """Test that agent config can generate system prompts."""
        from sunona.models import CreateAgentRequest
        
        request = CreateAgentRequest(
            agent_name=sample_agent_config["agent_name"],
            agent_type=sample_agent_config["agent_type"],
            agent_welcome_message=sample_agent_config["agent_welcome_message"]
        )
        
        assert request.agent_name == "Test Agent"
        assert request.agent_welcome_message is not None


class TestHealthCheckModels:
    """Tests for health check models."""
    
    def test_component_health(self):
        """Test ComponentHealth model."""
        from sunona.models import ComponentHealth
        
        health = ComponentHealth(
            name="redis",
            status="healthy",
            latency_ms=1.5
        )
        
        assert health.name == "redis"
        assert health.status == "healthy"
        assert health.latency_ms == 1.5
    
    def test_health_status(self):
        """Test HealthStatus model."""
        from sunona.models import HealthStatus
        
        status = HealthStatus(
            status="healthy",
            version="0.2.0"
        )
        
        assert status.status == "healthy"
        assert status.version == "0.2.0"


class TestModelSerialization:
    """Tests for model serialization/deserialization."""
    
    def test_transcriber_to_dict(self):
        """Test Transcriber model can be serialized to dict."""
        from sunona.models import Transcriber
        
        transcriber = Transcriber(provider="deepgram", model="nova-2")
        data = transcriber.model_dump()
        
        assert isinstance(data, dict)
        assert data["provider"] == "deepgram"
        assert data["model"] == "nova-2"
    
    def test_transcriber_from_dict(self):
        """Test Transcriber model can be created from dict."""
        from sunona.models import Transcriber
        
        data = {
            "provider": "groq",
            "model": "whisper-large-v3",
            "language": "en"
        }
        
        transcriber = Transcriber(**data)
        
        assert transcriber.provider == "groq"
        assert transcriber.model == "whisper-large-v3"
    
    def test_llm_config_json_roundtrip(self):
        """Test LLMConfig JSON serialization roundtrip."""
        from sunona.models import LLMConfig
        import json
        
        original = LLMConfig(
            provider="openrouter",
            model="mistralai/mistral-7b-instruct:free",
            temperature=0.7
        )
        
        json_str = original.model_dump_json()
        data = json.loads(json_str)
        restored = LLMConfig(**data)
        
        assert restored.provider == original.provider
        assert restored.model == original.model
        assert restored.temperature == original.temperature
