"""
Sunona Voice AI - No-Code Agent Builder

REST API and models for the no-code agent builder.
Enables drag-and-drop agent creation without coding.

Features:
- Agent templates
- Visual configuration
- Provider selection
- Prompt engineering UI support
- Preview/testing
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentTemplateCategory(Enum):
    """Categories for agent templates."""
    CUSTOMER_SERVICE = "customer_service"
    SALES = "sales"
    APPOINTMENT = "appointment"
    FAQ = "faq"
    SURVEY = "survey"
    IVR = "ivr"
    CUSTOM = "custom"


@dataclass
class AgentTemplate:
    """
    Pre-built agent template for quick setup.
    
    Users can start from a template and customize.
    """
    id: str
    name: str
    description: str
    category: AgentTemplateCategory
    
    # Default configuration
    agent_type: str = "contextual"
    default_prompt: str = ""
    default_voice: str = "alloy"
    default_language: str = "en"
    
    # Feature flags
    supports_extraction: bool = False
    supports_knowledge_base: bool = False
    supports_transfer: bool = True
    
    # Example use cases
    use_cases: List[str] = field(default_factory=list)
    
    # Recommended providers
    recommended_stt: str = "deepgram"
    recommended_llm: str = "openai/gpt-4o-mini"
    recommended_tts: str = "elevenlabs"
    
    # Visual settings
    icon: str = "🤖"
    color: str = "#4F46E5"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "agent_type": self.agent_type,
            "default_prompt": self.default_prompt,
            "default_voice": self.default_voice,
            "default_language": self.default_language,
            "supports_extraction": self.supports_extraction,
            "supports_knowledge_base": self.supports_knowledge_base,
            "supports_transfer": self.supports_transfer,
            "use_cases": self.use_cases,
            "recommended_providers": {
                "stt": self.recommended_stt,
                "llm": self.recommended_llm,
                "tts": self.recommended_tts,
            },
            "icon": self.icon,
            "color": self.color,
        }


@dataclass
class ProviderOption:
    """Provider option for UI selection."""
    id: str
    name: str
    type: str  # stt, llm, tts, telephony
    logo_url: Optional[str] = None
    
    # Capabilities
    streaming: bool = True
    languages: List[str] = field(default_factory=list)
    voices: List[Dict[str, str]] = field(default_factory=list)
    models: List[Dict[str, str]] = field(default_factory=list)
    
    # Pricing (for cost estimation)
    cost_per_minute: float = 0.0
    cost_per_1k_chars: float = 0.0
    cost_per_1k_tokens: float = 0.0
    
    # Quality metrics
    quality_score: float = 0.0  # 0-100
    latency_ms: float = 0.0
    
    # Requirements
    requires_api_key: bool = True
    api_key_env_var: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "logo_url": self.logo_url,
            "streaming": self.streaming,
            "languages": self.languages,
            "voices": self.voices,
            "models": self.models,
            "pricing": {
                "cost_per_minute": self.cost_per_minute,
                "cost_per_1k_chars": self.cost_per_1k_chars,
                "cost_per_1k_tokens": self.cost_per_1k_tokens,
            },
            "quality_score": self.quality_score,
            "latency_ms": self.latency_ms,
            "requires_api_key": self.requires_api_key,
        }


@dataclass
class AgentBuilderConfig:
    """
    Configuration being built in the no-code UI.
    
    Represents the state of the agent builder form.
    """
    # Identity
    id: str = ""
    name: str = "New Agent"
    description: str = ""
    
    # Template (if started from template)
    template_id: Optional[str] = None
    
    # Agent type
    agent_type: str = "contextual"
    
    # Prompt
    system_prompt: str = ""
    welcome_message: str = "Hello! How can I help you today?"
    
    # Voice settings
    voice_id: str = "alloy"
    voice_name: str = "Alloy"
    language: str = "en"
    speaking_rate: float = 1.0
    
    # Providers
    stt_provider: str = "deepgram"
    stt_model: str = "nova-2"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    tts_provider: str = "elevenlabs"
    tts_model: str = "eleven_turbo_v2_5"
    
    # Features
    enable_interruption: bool = True
    enable_transfer: bool = False
    transfer_number: str = ""
    enable_recording: bool = False
    enable_knowledge_base: bool = False
    knowledge_base_id: Optional[str] = None
    
    # Tools
    enabled_tools: List[str] = field(default_factory=list)
    
    # Advanced
    max_call_duration: int = 600  # seconds
    silence_timeout: int = 10
    temperature: float = 0.7
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    organization_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "template_id": self.template_id,
            "agent_type": self.agent_type,
            "system_prompt": self.system_prompt,
            "welcome_message": self.welcome_message,
            "voice": {
                "id": self.voice_id,
                "name": self.voice_name,
                "language": self.language,
                "speaking_rate": self.speaking_rate,
            },
            "providers": {
                "stt": {"provider": self.stt_provider, "model": self.stt_model},
                "llm": {"provider": self.llm_provider, "model": self.llm_model},
                "tts": {"provider": self.tts_provider, "model": self.tts_model},
            },
            "features": {
                "interruption": self.enable_interruption,
                "transfer": self.enable_transfer,
                "transfer_number": self.transfer_number,
                "recording": self.enable_recording,
                "knowledge_base": self.enable_knowledge_base,
                "knowledge_base_id": self.knowledge_base_id,
            },
            "tools": self.enabled_tools,
            "advanced": {
                "max_call_duration": self.max_call_duration,
                "silence_timeout": self.silence_timeout,
                "temperature": self.temperature,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "organization_id": self.organization_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentBuilderConfig":
        """Create config from dictionary."""
        config = cls()
        config.id = data.get("id", "")
        config.name = data.get("name", "New Agent")
        config.description = data.get("description", "")
        config.template_id = data.get("template_id")
        config.agent_type = data.get("agent_type", "contextual")
        config.system_prompt = data.get("system_prompt", "")
        config.welcome_message = data.get("welcome_message", "")
        
        voice = data.get("voice", {})
        config.voice_id = voice.get("id", "alloy")
        config.voice_name = voice.get("name", "Alloy")
        config.language = voice.get("language", "en")
        config.speaking_rate = voice.get("speaking_rate", 1.0)
        
        providers = data.get("providers", {})
        stt = providers.get("stt", {})
        config.stt_provider = stt.get("provider", "deepgram")
        config.stt_model = stt.get("model", "nova-2")
        
        llm = providers.get("llm", {})
        config.llm_provider = llm.get("provider", "openai")
        config.llm_model = llm.get("model", "gpt-4o-mini")
        
        tts = providers.get("tts", {})
        config.tts_provider = tts.get("provider", "elevenlabs")
        config.tts_model = tts.get("model", "eleven_turbo_v2_5")
        
        features = data.get("features", {})
        config.enable_interruption = features.get("interruption", True)
        config.enable_transfer = features.get("transfer", False)
        config.transfer_number = features.get("transfer_number", "")
        config.enable_recording = features.get("recording", False)
        config.enable_knowledge_base = features.get("knowledge_base", False)
        config.knowledge_base_id = features.get("knowledge_base_id")
        
        config.enabled_tools = data.get("tools", [])
        
        advanced = data.get("advanced", {})
        config.max_call_duration = advanced.get("max_call_duration", 600)
        config.silence_timeout = advanced.get("silence_timeout", 10)
        config.temperature = advanced.get("temperature", 0.7)
        
        config.organization_id = data.get("organization_id")
        
        return config


class AgentBuilder:
    """
    Agent builder service for no-code UI.
    
    Provides APIs for:
    - Listing templates
    - Listing providers/voices
    - Creating/updating agent configs
    - Converting to deployable agents
    
    Example:
        builder = AgentBuilder()
        
        # Get templates
        templates = await builder.list_templates()
        
        # Create from template
        config = await builder.create_from_template("customer_service_basic")
        
        # Update config
        config.name = "My Customer Service Agent"
        config.system_prompt = "You are a helpful..."
        
        # Deploy
        agent = await builder.deploy(config)
    """
    
    def __init__(self):
        self._templates: Dict[str, AgentTemplate] = {}
        self._providers: Dict[str, ProviderOption] = {}
        self._configs: Dict[str, AgentBuilderConfig] = {}
        
        # Initialize with defaults
        self._init_default_templates()
        self._init_default_providers()
    
    def _init_default_templates(self) -> None:
        """Initialize default agent templates."""
        templates = [
            AgentTemplate(
                id="customer_service_basic",
                name="Customer Service Agent",
                description="Handle customer inquiries, complaints, and support requests",
                category=AgentTemplateCategory.CUSTOMER_SERVICE,
                agent_type="contextual",
                default_prompt=(
                    "You are a helpful customer service agent. Be friendly, professional, "
                    "and empathetic. Help customers with their questions and concerns. "
                    "If you cannot help, offer to transfer them to a human agent."
                ),
                default_voice="alloy",
                supports_knowledge_base=True,
                supports_transfer=True,
                use_cases=[
                    "Answer product questions",
                    "Handle complaints",
                    "Check order status",
                    "Process returns",
                ],
                icon="🎧",
                color="#10B981",
            ),
            AgentTemplate(
                id="appointment_scheduler",
                name="Appointment Scheduler",
                description="Book, reschedule, and cancel appointments",
                category=AgentTemplateCategory.APPOINTMENT,
                agent_type="extraction",
                default_prompt=(
                    "You are an appointment scheduling assistant. Help callers book, "
                    "reschedule, or cancel appointments. Collect necessary information: "
                    "name, contact number, preferred date and time, and reason for visit."
                ),
                supports_extraction=True,
                use_cases=[
                    "Book new appointments",
                    "Reschedule existing appointments",
                    "Cancel appointments",
                    "Check availability",
                ],
                icon="📅",
                color="#6366F1",
            ),
            AgentTemplate(
                id="lead_qualifier",
                name="Lead Qualification Agent",
                description="Qualify sales leads with structured questions",
                category=AgentTemplateCategory.SALES,
                agent_type="extraction",
                default_prompt=(
                    "You are a sales qualification agent. Your goal is to qualify leads "
                    "by asking about their needs, budget, timeline, and decision-making "
                    "process. Be professional and consultative."
                ),
                supports_extraction=True,
                supports_transfer=True,
                use_cases=[
                    "Qualify inbound leads",
                    "Schedule sales demos",
                    "Collect contact information",
                    "Understand requirements",
                ],
                icon="💼",
                color="#F59E0B",
            ),
            AgentTemplate(
                id="faq_bot",
                name="FAQ Knowledge Bot",
                description="Answer questions from a knowledge base",
                category=AgentTemplateCategory.FAQ,
                agent_type="knowledgebase",
                default_prompt=(
                    "You are a knowledgeable assistant. Answer questions based on "
                    "the provided knowledge base. If you don't know the answer, "
                    "say so honestly and offer to connect with a human."
                ),
                supports_knowledge_base=True,
                use_cases=[
                    "Answer product FAQs",
                    "Provide documentation help",
                    "Technical support",
                ],
                icon="📚",
                color="#EC4899",
            ),
            AgentTemplate(
                id="survey_agent",
                name="Survey Agent",
                description="Conduct phone surveys and collect feedback",
                category=AgentTemplateCategory.SURVEY,
                agent_type="extraction",
                default_prompt=(
                    "You are conducting a customer satisfaction survey. Be polite "
                    "and professional. Ask questions one at a time and wait for "
                    "responses. Thank the caller for their time."
                ),
                supports_extraction=True,
                use_cases=[
                    "Customer satisfaction surveys",
                    "NPS collection",
                    "Market research",
                    "Feedback collection",
                ],
                icon="📊",
                color="#8B5CF6",
            ),
            AgentTemplate(
                id="ivr_menu",
                name="IVR Menu System",
                description="Route calls with an intelligent voice menu",
                category=AgentTemplateCategory.IVR,
                agent_type="graph",
                default_prompt=(
                    "You are a phone menu system. Help callers navigate to the "
                    "right department. Understand natural language requests like "
                    "'I want to talk to sales' or 'I have a billing question'."
                ),
                supports_transfer=True,
                use_cases=[
                    "Call routing",
                    "Department selection",
                    "After-hours handling",
                ],
                icon="📞",
                color="#14B8A6",
            ),
        ]
        
        for template in templates:
            self._templates[template.id] = template
    
    def _init_default_providers(self) -> None:
        """Initialize provider options."""
        # STT Providers
        stt_providers = [
            ProviderOption(
                id="deepgram",
                name="Deepgram",
                type="stt",
                streaming=True,
                languages=["en", "es", "fr", "de", "it", "pt", "hi", "ja", "ko", "zh"],
                models=[
                    {"id": "nova-2", "name": "Nova 2 (Recommended)"},
                    {"id": "nova", "name": "Nova"},
                    {"id": "enhanced", "name": "Enhanced"},
                ],
                cost_per_minute=0.0043,
                quality_score=95,
                latency_ms=200,
                api_key_env_var="DEEPGRAM_API_KEY",
            ),
            ProviderOption(
                id="azure",
                name="Azure Speech",
                type="stt",
                streaming=True,
                languages=["en", "es", "fr", "de", "it", "pt", "hi", "ja", "ko", "zh", "ar"],
                models=[
                    {"id": "default", "name": "Azure Speech"},
                ],
                cost_per_minute=0.0048,
                quality_score=90,
                latency_ms=250,
                api_key_env_var="AZURE_SPEECH_KEY",
            ),
            ProviderOption(
                id="assembly",
                name="AssemblyAI",
                type="stt",
                streaming=True,
                languages=["en", "es", "fr", "de", "it"],
                models=[
                    {"id": "best", "name": "Best"},
                    {"id": "nano", "name": "Nano (Fast)"},
                ],
                cost_per_minute=0.006,
                quality_score=92,
                latency_ms=300,
                api_key_env_var="ASSEMBLY_API_KEY",
            ),
        ]
        
        # TTS Providers
        tts_providers = [
            ProviderOption(
                id="elevenlabs",
                name="ElevenLabs",
                type="tts",
                streaming=True,
                voices=[
                    {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
                    {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
                    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
                    {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
                    {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli"},
                    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"},
                ],
                cost_per_1k_chars=0.30,
                quality_score=98,
                latency_ms=150,
                api_key_env_var="ELEVENLABS_API_KEY",
            ),
            ProviderOption(
                id="openai",
                name="OpenAI TTS",
                type="tts",
                streaming=True,
                voices=[
                    {"id": "alloy", "name": "Alloy"},
                    {"id": "echo", "name": "Echo"},
                    {"id": "fable", "name": "Fable"},
                    {"id": "onyx", "name": "Onyx"},
                    {"id": "nova", "name": "Nova"},
                    {"id": "shimmer", "name": "Shimmer"},
                ],
                cost_per_1k_chars=0.015,
                quality_score=90,
                latency_ms=200,
                api_key_env_var="OPENAI_API_KEY",
            ),
            ProviderOption(
                id="cartesia",
                name="Cartesia",
                type="tts",
                streaming=True,
                voices=[
                    {"id": "sonic-english-alpha", "name": "Sonic English Alpha"},
                ],
                cost_per_1k_chars=0.05,
                quality_score=92,
                latency_ms=100,
                api_key_env_var="CARTESIA_API_KEY",
            ),
        ]
        
        # LLM Providers
        llm_providers = [
            ProviderOption(
                id="openai",
                name="OpenAI",
                type="llm",
                streaming=True,
                models=[
                    {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Recommended)"},
                    {"id": "gpt-4o", "name": "GPT-4o"},
                    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
                ],
                cost_per_1k_tokens=0.00015,
                quality_score=95,
                latency_ms=300,
                api_key_env_var="OPENAI_API_KEY",
            ),
            ProviderOption(
                id="anthropic",
                name="Anthropic Claude",
                type="llm",
                streaming=True,
                models=[
                    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku (Fast)"},
                ],
                cost_per_1k_tokens=0.003,
                quality_score=96,
                latency_ms=350,
                api_key_env_var="ANTHROPIC_API_KEY",
            ),
            ProviderOption(
                id="groq",
                name="Groq",
                type="llm",
                streaming=True,
                models=[
                    {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
                    {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B (Fast)"},
                    {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B"},
                ],
                cost_per_1k_tokens=0.0001,
                quality_score=88,
                latency_ms=100,
                api_key_env_var="GROQ_API_KEY",
            ),
            ProviderOption(
                id="openrouter",
                name="OpenRouter (Free Models)",
                type="llm",
                streaming=True,
                models=[
                    {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (FREE)"},
                    {"id": "meta-llama/llama-3.2-3b-instruct:free", "name": "Llama 3.2 3B (FREE)"},
                    {"id": "qwen/qwen-2-7b-instruct:free", "name": "Qwen 2 7B (FREE)"},
                ],
                cost_per_1k_tokens=0.0,
                quality_score=80,
                latency_ms=400,
                api_key_env_var="OPENROUTER_API_KEY",
            ),
        ]
        
        for p in stt_providers + tts_providers + llm_providers:
            self._providers[p.id] = p
    
    async def list_templates(
        self,
        category: Optional[AgentTemplateCategory] = None,
    ) -> List[AgentTemplate]:
        """List available agent templates."""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    async def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get a specific template."""
        return self._templates.get(template_id)
    
    async def list_providers(
        self,
        provider_type: Optional[str] = None,
    ) -> List[ProviderOption]:
        """List available providers."""
        providers = list(self._providers.values())
        
        if provider_type:
            providers = [p for p in providers if p.type == provider_type]
        
        return providers
    
    async def create_from_template(
        self,
        template_id: str,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> AgentBuilderConfig:
        """Create a new agent config from a template."""
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")
        
        config = AgentBuilderConfig(
            id=f"draft_{uuid.uuid4().hex}",
            name=f"New {template.name}",
            template_id=template_id,
            agent_type=template.agent_type,
            system_prompt=template.default_prompt,
            voice_id=template.default_voice,
            language=template.default_language,
            stt_provider=template.recommended_stt,
            llm_provider=template.recommended_llm.split("/")[0],
            llm_model=template.recommended_llm.split("/")[-1],
            tts_provider=template.recommended_tts,
            enable_knowledge_base=template.supports_knowledge_base,
            enable_transfer=template.supports_transfer,
            organization_id=organization_id,
            created_by=created_by,
        )
        
        self._configs[config.id] = config
        return config
    
    async def create_blank(
        self,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> AgentBuilderConfig:
        """Create a blank agent config."""
        config = AgentBuilderConfig(
            id=f"draft_{uuid.uuid4().hex}",
            organization_id=organization_id,
            created_by=created_by,
        )
        
        self._configs[config.id] = config
        return config
    
    async def get_config(self, config_id: str) -> Optional[AgentBuilderConfig]:
        """Get an agent builder config."""
        return self._configs.get(config_id)
    
    async def update_config(
        self,
        config_id: str,
        updates: Dict[str, Any],
    ) -> Optional[AgentBuilderConfig]:
        """Update an agent builder config."""
        config = self._configs.get(config_id)
        if not config:
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.updated_at = datetime.now(timezone.utc)
        return config
    
    async def save_config(
        self,
        config: AgentBuilderConfig,
    ) -> AgentBuilderConfig:
        """Save an agent builder config."""
        config.updated_at = datetime.now(timezone.utc)
        self._configs[config.id] = config
        return config
    
    async def delete_config(self, config_id: str) -> bool:
        """Delete an agent builder config."""
        if config_id in self._configs:
            del self._configs[config_id]
            return True
        return False
    
    async def list_configs(
        self,
        organization_id: Optional[str] = None,
    ) -> List[AgentBuilderConfig]:
        """List all configs, optionally filtered by organization."""
        configs = list(self._configs.values())
        
        if organization_id:
            configs = [c for c in configs if c.organization_id == organization_id]
        
        return configs
    
    async def deploy(
        self,
        config_id: str,
    ) -> Dict[str, Any]:
        """
        Deploy an agent from the builder config.
        
        Converts the builder config to a deployable agent configuration.
        """
        config = self._configs.get(config_id)
        if not config:
            raise ValueError(f"Config '{config_id}' not found")
        
        # Generate deployable agent config
        agent_config = {
            "agent_name": config.name,
            "agent_type": config.agent_type,
            "tasks": [
                {
                    "task_type": "conversation",
                    "toolchain": {
                        "execution": "parallel",
                        "pipelines": [["transcriber", "llm", "synthesizer"]],
                    },
                    "tools_config": {
                        "transcriber": {
                            "provider": config.stt_provider,
                            "model": config.stt_model,
                            "language": config.language,
                            "stream": True,
                        },
                        "llm_agent": {
                            "agent_type": config.agent_type + "_agent",
                            "llm_config": {
                                "provider": config.llm_provider,
                                "model": config.llm_model,
                                "temperature": config.temperature,
                            },
                        },
                        "synthesizer": {
                            "provider": config.tts_provider,
                            "model": config.tts_model,
                            "voice": config.voice_id,
                            "stream": True,
                        },
                    },
                    "task_config": {
                        "hangup_after_silence": config.silence_timeout,
                        "max_duration": config.max_call_duration,
                    },
                },
            ],
            "agent_welcome_message": config.welcome_message,
            "agent_prompts": {
                "task_1": {
                    "system_prompt": config.system_prompt,
                },
            },
        }
        
        # Add optional features
        if config.enable_knowledge_base and config.knowledge_base_id:
            agent_config["knowledge_base_id"] = config.knowledge_base_id
        
        if config.enable_transfer:
            agent_config["transfer_config"] = {
                "enabled": True,
                "transfer_number": config.transfer_number,
            }
        
        if config.enable_recording:
            agent_config["recording"] = {"enabled": True}
        
        if config.enabled_tools:
            agent_config["tools"] = config.enabled_tools
        
        logger.info(f"Deployed agent from config {config_id}")
        
        return agent_config
    
    async def estimate_cost(
        self,
        config_id: str,
        minutes_per_month: int = 100,
    ) -> Dict[str, Any]:
        """Estimate monthly cost for an agent configuration."""
        config = self._configs.get(config_id)
        if not config:
            return {"error": "Config not found"}
        
        # Get provider costs
        stt = self._providers.get(config.stt_provider)
        tts = self._providers.get(config.tts_provider)
        llm = self._providers.get(config.llm_provider)
        
        # Estimate usage
        avg_words_per_minute = 150
        avg_chars_per_word = 5
        avg_tokens_per_word = 1.3
        
        chars_per_month = minutes_per_month * avg_words_per_minute * avg_chars_per_word
        tokens_per_month = minutes_per_month * avg_words_per_minute * avg_tokens_per_word
        
        # Calculate costs
        stt_cost = (stt.cost_per_minute * minutes_per_month) if stt else 0
        tts_cost = (tts.cost_per_1k_chars * chars_per_month / 1000) if tts else 0
        llm_cost = (llm.cost_per_1k_tokens * tokens_per_month / 1000) if llm else 0
        
        total = stt_cost + tts_cost + llm_cost
        
        return {
            "minutes_per_month": minutes_per_month,
            "breakdown": {
                "stt": {"provider": config.stt_provider, "cost": round(stt_cost, 2)},
                "tts": {"provider": config.tts_provider, "cost": round(tts_cost, 2)},
                "llm": {"provider": config.llm_provider, "cost": round(llm_cost, 2)},
            },
            "total_monthly_cost": round(total, 2),
            "cost_per_minute": round(total / minutes_per_month, 4) if minutes_per_month > 0 else 0,
        }


# Global builder instance
_global_builder: Optional[AgentBuilder] = None


def get_agent_builder() -> AgentBuilder:
    """Get or create global agent builder."""
    global _global_builder
    if _global_builder is None:
        _global_builder = AgentBuilder()
    return _global_builder
