"""
Sunona Voice AI - Data Models

Comprehensive Pydantic models for the entire platform.
Includes configurations for all providers, agents, and features.
"""

import json
from typing import Optional, List, Union, Dict, Callable, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum


# ==================== SUPPORTED PROVIDERS ====================
# Defined here to avoid circular imports with providers.py

SUPPORTED_TRANSCRIBER_NAMES = [
    "deepgram", "azure", "sarvam", "assembly", "google",
    "pixa", "gladia", "elevenlabs", "smallest", "groq", "whisper"
]

SUPPORTED_SYNTHESIZER_NAMES = [
    "polly", "elevenlabs", "azuretts", "openai", "deepgram",
    "cartesia", "smallest", "sarvam", "rime", "playht"
]


# ==================== CONSTANTS ====================

AGENT_WELCOME_MESSAGE = "Hello! How can I help you today?"

# More natural welcome messages
WELCOME_MESSAGES = {
    "default": "Hello! How can I help you today?",
    "support": "Hi there! Thanks for calling support. How can I help?",
    "sales": "Hello! Thanks for your interest. What can I tell you about our products?",
    "appointment": "Hi! I can help you schedule an appointment. When works best for you?",
    "recording": "This call may be recorded for quality purposes. How can I assist you?",
}


# ==================== HELPER FUNCTIONS ====================

def validate_attribute(value, allowed_values, value_type='provider'):
    """Validate that a value is in the allowed list."""
    if value not in allowed_values:
        raise ValueError(f"Invalid {value_type}: '{value}'. Supported: {allowed_values}")
    return value


# ==================== ENUMS ====================

class AgentType(str, Enum):
    """Types of agents available."""
    CONTEXTUAL = "contextual"
    EXTRACTION = "extraction"
    GRAPH = "graph"
    GRAPH_CONVERSATIONAL = "graph_conversational"
    KNOWLEDGE_BASE = "knowledge_base"
    SUMMARIZATION = "summarization"
    WEBHOOK = "webhook"
    SIMPLE = "simple_llm_agent"
    MULTI = "multiagent"


class TaskType(str, Enum):
    """Types of tasks."""
    CONVERSATION = "conversation"
    EXTRACTION = "extraction"
    SUMMARIZATION = "summarization"
    NOTIFICATION = "notification"
    SURVEY = "survey"
    APPOINTMENT = "appointment"


class FlowType(str, Enum):
    """Agent flow types."""
    STREAMING = "streaming"
    BATCH = "batch"
    WEBSOCKET = "websocket"


# ==================== TTS PROVIDER CONFIGS ====================

class PollyConfig(BaseModel):
    """Amazon Polly TTS configuration."""
    voice: str = "Joanna"
    engine: str = "neural"
    language: str = "en-US"
    
    model_config = ConfigDict(extra="allow")


class ElevenLabsConfig(BaseModel):
    """ElevenLabs TTS configuration - Premium quality voices."""
    voice: str = "Sarah"
    voice_id: str = "EXAVITQu4vr4xnSDxMaL"
    model: str = "eleven_turbo_v2_5"
    temperature: float = 0.5
    similarity_boost: float = 0.75
    speed: float = 1.0
    style: float = 0.0
    
    # Emotional settings for better UX
    stability: float = 0.5
    use_speaker_boost: bool = True
    
    model_config = ConfigDict(extra="allow")


class OpenAITTSConfig(BaseModel):
    """OpenAI TTS configuration."""
    voice: str = "alloy"
    model: str = "tts-1"
    speed: float = 1.0
    
    model_config = ConfigDict(extra="allow")


class DeepgramTTSConfig(BaseModel):
    """Deepgram Aura TTS configuration - Low latency."""
    voice_id: str = "aura-asteria-en"
    voice: str = "asteria"
    model: str = "aura"
    
    model_config = ConfigDict(extra="allow")


class CartesiaConfig(BaseModel):
    """Cartesia TTS configuration."""
    voice_id: str
    voice: str
    model: str = "sonic-english"
    language: str = "en"
    
    model_config = ConfigDict(extra="allow")


class RimeConfig(BaseModel):
    """Rime TTS configuration."""
    voice_id: str
    language: str = "en"
    voice: str
    model: str = "mist"
    
    model_config = ConfigDict(extra="allow")


class SmallestConfig(BaseModel):
    """Smallest AI TTS configuration."""
    voice_id: str
    language: str = "en"
    voice: str
    model: str = "lightning"
    
    model_config = ConfigDict(extra="allow")


class SarvamConfig(BaseModel):
    """Sarvam AI TTS configuration (Indian languages)."""
    voice_id: str
    language: str = "hi-IN"
    voice: str
    model: str = "bulbul:v1"
    speed: float = 1.0
    
    model_config = ConfigDict(extra="allow")


class AzureTTSConfig(BaseModel):
    """Azure TTS configuration."""
    voice: str = "en-US-JennyNeural"
    model: str = "neural"
    language: str = "en-US"
    speed: float = 1.0
    
    model_config = ConfigDict(extra="allow")


class PlayHTConfig(BaseModel):
    """PlayHT TTS configuration."""
    voice_id: str
    voice: str
    model: str = "Play3.0-mini"
    speed: float = 1.0
    
    model_config = ConfigDict(extra="allow")


# ==================== TRANSCRIBER ====================

class Transcriber(BaseModel):
    """Speech-to-text transcriber configuration."""
    model: str = "nova-2"
    language: Optional[str] = None
    stream: bool = True
    sampling_rate: int = 16000
    encoding: str = "linear16"
    endpointing: int = 500
    keywords: Optional[str] = None
    task: str = "transcribe"
    provider: str = "deepgram"
    
    # Enhanced settings
    smart_format: bool = True
    punctuate: bool = True
    profanity_filter: bool = False
    diarize: bool = False
    
    model_config = ConfigDict(extra="allow")

    @field_validator("provider")
    def validate_provider(cls, value):
        return validate_attribute(value, SUPPORTED_TRANSCRIBER_NAMES, "transcriber provider")


# ==================== SYNTHESIZER ====================

# Type alias for provider configs
TTSProviderConfig = Union[
    PollyConfig, ElevenLabsConfig, AzureTTSConfig, RimeConfig,
    SmallestConfig, SarvamConfig, CartesiaConfig, DeepgramTTSConfig,
    OpenAITTSConfig, PlayHTConfig
]


class Synthesizer(BaseModel):
    """Text-to-speech synthesizer configuration."""
    provider: str = "elevenlabs"
    provider_config: TTSProviderConfig = Field(
        default_factory=lambda: ElevenLabsConfig(),
        union_mode='smart'
    )
    stream: bool = True
    buffer_size: int = 40  # Characters in buffer
    audio_format: str = "pcm"
    caching: bool = True
    
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    def preprocess(cls, values):
        provider = values.get("provider", "elevenlabs")
        config = values.get("provider_config", {})

        if provider == "elevenlabs" and isinstance(config, dict):
            if not config.get("voice_id"):
                config["voice_id"] = "EXAVITQu4vr4xnSDxMaL"
            if not config.get("voice"):
                config["voice"] = "Sarah"
            values["provider_config"] = config

        return values

    @field_validator("provider")
    def validate_provider(cls, value):
        allowed = [
            "polly", "elevenlabs", "azuretts", "openai", "deepgram",
            "cartesia", "smallest", "sarvam", "rime", "playht"
        ]
        return validate_attribute(value, allowed, "TTS provider")


# ==================== IO MODELS ====================

class IOModel(BaseModel):
    """
    Input/Output configuration for telephony.
    
    Defaults to 'default' handler. Only specify 'twilio', 'plivo', or 'exotel'
    when using actual telephony integration.
    """
    provider: str = "default"  # Default to no telephony unless specified
    format: str = "wav"
    
    model_config = ConfigDict(extra="allow")

    @field_validator("provider")
    def validate_provider(cls, value):
        allowed = ["default", "twilio", "plivo", "exotel", "database", "vonage", "telnyx"]
        return validate_attribute(value, allowed, "IO provider")


# ==================== ROUTING ====================

class Route(BaseModel):
    """Route configuration for intent matching."""
    route_name: str
    utterances: List[str]
    response: Union[List[str], str]
    score_threshold: float = 0.85
    
    model_config = ConfigDict(extra="allow")


class Routes(BaseModel):
    """Routes for FAQs, prompt routing, guardrails."""
    embedding_model: str = "Snowflake/snowflake-arctic-embed-l"
    routes: List[Route] = []
    
    model_config = ConfigDict(extra="allow")


# ==================== RAG / VECTOR STORES ====================

class RerankerConfig(BaseModel):
    """Reranker configuration for improved RAG results."""
    enabled: bool = False
    reranker_type: str = "minilm-l6-v2"  # Renamed from model_type to avoid Pydantic namespace conflict
    candidate_count: int = 20
    final_count: int = 5
    
    model_config = ConfigDict(extra="allow", protected_namespaces=())

    @field_validator("reranker_type")
    def validate_model(cls, value):
        allowed = ["bge-base", "bge-large", "bge-multilingual", "minilm-l6-v2"]
        return validate_attribute(value, allowed, "reranker model")

    @field_validator("candidate_count")
    def validate_candidates(cls, value):
        if not 1 <= value <= 100:
            raise ValueError("candidate_count must be 1-100")
        return value

    @field_validator("final_count")
    def validate_final(cls, value):
        if not 1 <= value <= 50:
            raise ValueError("final_count must be 1-50")
        return value


class LanceDBProviderConfig(BaseModel):
    """LanceDB vector store configuration."""
    vector_id: str
    similarity_top_k: int = 5
    score_threshold: float = 0.1
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    
    model_config = ConfigDict(extra="allow")


class MongoDBProviderConfig(BaseModel):
    """MongoDB vector store configuration."""
    connection_string: Optional[str] = None
    db_name: Optional[str] = None
    collection_name: Optional[str] = None
    index_name: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 256
    
    model_config = ConfigDict(extra="allow")


class ChromaDBConfig(BaseModel):
    """ChromaDB vector store configuration."""
    collection_name: str
    persist_directory: Optional[str] = None
    embedding_function: str = "default"
    
    model_config = ConfigDict(extra="allow")


class PineconeConfig(BaseModel):
    """Pinecone vector store configuration."""
    index_name: str
    namespace: Optional[str] = None
    top_k: int = 5
    
    model_config = ConfigDict(extra="allow")


class VectorStore(BaseModel):
    """Vector store configuration for RAG."""
    provider: str = "lancedb"
    provider_config: Union[LanceDBProviderConfig, MongoDBProviderConfig, ChromaDBConfig, PineconeConfig]
    
    model_config = ConfigDict(extra="allow")


# ==================== LLM CONFIGURATION ====================

class Llm(BaseModel):
    """LLM configuration with smart defaults."""
    model: str = "gpt-4o-mini"
    max_tokens: int = 500
    family: str = "openai"
    temperature: float = 0.7
    request_json: bool = False
    stop: Optional[List[str]] = None
    top_k: int = 0
    top_p: float = 0.9
    min_p: float = 0.1
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    provider: str = "openai"
    base_url: Optional[str] = None
    routes: Optional[Routes] = None
    
    # Smart model selection
    balance_aware: bool = True
    fallback_model: str = "mistralai/mistral-7b-instruct:free"
    
    model_config = ConfigDict(extra="allow")


class SimpleLlmAgent(Llm):
    """Simple LLM agent configuration."""
    agent_flow_type: str = "streaming"
    routes: Optional[Routes] = None
    extraction_details: Optional[str] = None
    summarization_details: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


# ==================== GRAPH AGENT ====================

class GraphEdge(BaseModel):
    """Edge connecting graph nodes."""
    to_node_id: str
    condition: str
    
    model_config = ConfigDict(extra="allow")


class GraphNodeRAGConfig(BaseModel):
    """RAG configuration for graph nodes."""
    vector_store: VectorStore
    temperature: float = 0.7
    model: str = "gpt-4o-mini"
    max_tokens: int = 150
    
    model_config = ConfigDict(extra="allow")


class GraphNode(BaseModel):
    """Node in conversation graph."""
    id: str
    description: Optional[str] = None
    prompt: str
    edges: List[GraphEdge] = Field(default_factory=list)
    completion_check: Optional[Callable[[List[dict]], bool]] = None
    rag_config: Optional[GraphNodeRAGConfig] = None
    
    # Node behavior
    allow_llm_fallback: bool = True
    max_attempts: int = 3
    
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class Node(BaseModel):
    """Legacy node format for backward compatibility."""
    id: str
    type: str  # router or conversation
    llm: Llm
    exit_criteria: str
    exit_response: Optional[str] = None
    exit_prompt: Optional[str] = None
    is_root: bool = False
    
    model_config = ConfigDict(extra="allow")


class Edge(BaseModel):
    """Legacy edge format for backward compatibility."""
    start_node: str
    end_node: str
    condition: Optional[tuple] = None
    
    model_config = ConfigDict(extra="allow")


class LlmAgentGraph(BaseModel):
    """LLM agent graph configuration."""
    nodes: List[Node]
    edges: List[Edge]
    
    model_config = ConfigDict(extra="allow")


class GraphAgentConfig(Llm):
    """Graph agent configuration."""
    agent_information: str
    nodes: List[GraphNode]
    current_node_id: str
    context_data: Optional[dict] = None
    
    # Enhanced features
    allow_off_script: bool = True
    max_off_script_turns: int = 3
    
    model_config = ConfigDict(extra="allow")


# ==================== KNOWLEDGE BASE AGENT ====================

class KnowledgeAgentConfig(Llm):
    """Knowledge base agent configuration."""
    agent_information: str = "Knowledge-based AI assistant"
    prompt: Optional[str] = None
    rag_config: Optional[Dict] = None
    llm_provider: str = "openai"
    context_data: Optional[dict] = None
    
    # RAG behavior
    fallback_on_no_context: bool = True
    confidence_threshold: float = 0.5
    max_unknown_before_transfer: int = 2
    
    model_config = ConfigDict(extra="allow")


class KnowledgebaseAgent(Llm):
    """Knowledge base agent with vector store."""
    vector_store: VectorStore
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    
    model_config = ConfigDict(extra="allow")


# ==================== MULTI-AGENT ====================

class AgentRouteConfig(BaseModel):
    """Route configuration for multi-agent."""
    utterances: List[str]
    threshold: float = 0.85
    
    model_config = ConfigDict(extra="allow")


class MultiAgent(BaseModel):
    """Multi-agent router configuration."""
    agent_map: Dict[str, Llm]
    agent_routing_config: Dict[str, AgentRouteConfig]
    default_agent: str
    embedding_model: str = "Snowflake/snowflake-arctic-embed-l"
    
    model_config = ConfigDict(extra="allow")


# ==================== EXTRACTION AGENT ====================

class ExtractionField(BaseModel):
    """Field to extract from conversation."""
    name: str
    description: str
    field_type: str = "text"  # text, email, phone, date, number, boolean
    required: bool = False
    validation_regex: Optional[str] = None
    prompt_question: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class ExtractionAgentConfig(Llm):
    """Extraction agent configuration."""
    fields: List[ExtractionField] = []
    confirm_before_submit: bool = True
    allow_corrections: bool = True
    
    model_config = ConfigDict(extra="allow")


# ==================== UNIFIED AGENT CONFIG ====================

# Type alias for all agent configs
AgentConfigType = Union[
    KnowledgebaseAgent, LlmAgentGraph, MultiAgent, 
    SimpleLlmAgent, GraphAgentConfig, KnowledgeAgentConfig,
    ExtractionAgentConfig
]


class LlmAgent(BaseModel):
    """
    Unified LLM agent model.
    
    Can be instantiated with defaults:
        agent = LlmAgent()  # Uses SimpleLlmAgent with gpt-4o-mini
    
    Or with custom config:
        agent = LlmAgent(
            agent_type="extraction",
            llm_config={"model": "gpt-4o"}
        )
    """
    agent_flow_type: str = "streaming"
    agent_type: str = "simple_llm_agent"
    routes: Optional[Routes] = None
    llm_config: Optional[AgentConfigType] = Field(
        default_factory=SimpleLlmAgent,
        description="LLM configuration, defaults to SimpleLlmAgent"
    )
    
    # Smart agent selection
    auto_select_agent: bool = False
    
    model_config = ConfigDict(extra="allow")

    @field_validator('llm_config', mode='before')
    def validate_llm_config(cls, value, info):
        agent_type = info.data.get('agent_type', 'simple_llm_agent')

        config_types = {
            'knowledgebase_agent': KnowledgeAgentConfig,
            'knowledge_base': KnowledgeAgentConfig,
            'graph_agent': GraphAgentConfig,
            'llm_agent_graph': LlmAgentGraph,
            'multiagent': MultiAgent,
            'simple_llm_agent': SimpleLlmAgent,
            'extraction': ExtractionAgentConfig,
            'contextual': SimpleLlmAgent,
        }

        # Handle None - use default
        if value is None:
            return SimpleLlmAgent()

        if agent_type not in config_types:
            # Fallback to SimpleLlmAgent for unknown types
            expected_type = SimpleLlmAgent
        else:
            expected_type = config_types[agent_type]

        if isinstance(value, dict):
            try:
                return expected_type(**value)
            except Exception as e:
                raise ValueError(f"Failed to create {expected_type.__name__}: {e}")
        
        return value


# ==================== TOOLS ====================

class ToolFunction(BaseModel):
    """Function definition for tool calling."""
    name: str
    description: str
    parameters: Dict
    strict: bool = True
    
    model_config = ConfigDict(extra="allow")


class ToolDescription(BaseModel):
    """Tool description for LLM."""
    type: str = "function"
    function: ToolFunction
    
    model_config = ConfigDict(extra="allow")


class ToolDescriptionLegacy(BaseModel):
    """Legacy tool description format."""
    name: str
    description: str
    parameters: Dict
    
    model_config = ConfigDict(extra="allow")


class APIParams(BaseModel):
    """API parameters for tool execution."""
    url: Optional[str] = None
    method: str = "POST"
    api_token: Optional[str] = None
    param: Optional[Union[str, dict]] = None
    headers: Optional[Union[str, dict]] = None
    timeout: int = 30
    
    model_config = ConfigDict(extra="allow")


class ToolModel(BaseModel):
    """Tool model configuration."""
    tools: Optional[Union[str, List[Union[ToolDescription, ToolDescriptionLegacy]]]] = None
    tools_params: Dict[str, APIParams] = {}
    
    model_config = ConfigDict(extra="allow")


class ToolsChainModel(BaseModel):
    """Tool chain execution configuration."""
    execution: str = Field(..., pattern="^(parallel|sequential)$")
    pipelines: List[List[str]]
    
    model_config = ConfigDict(extra="allow")


# ==================== TOOLS CONFIG ====================

class ToolsConfig(BaseModel):
    """Complete tools configuration."""
    llm_agent: Optional[Union[LlmAgent, SimpleLlmAgent]] = None
    synthesizer: Optional[Synthesizer] = None
    transcriber: Optional[Transcriber] = None
    input: Optional[IOModel] = None
    output: Optional[IOModel] = None
    api_tools: Optional[ToolModel] = None
    
    model_config = ConfigDict(extra="allow")


# ==================== CONVERSATION CONFIG ====================

class ConversationConfig(BaseModel):
    """Conversation behavior configuration."""
    # Latency optimization
    optimize_latency: bool = True
    
    # Silence handling
    hangup_after_silence: int = 20
    incremental_delay: int = 900
    
    # Interruption handling
    number_of_words_for_interruption: int = 1
    interruption_backoff_period: int = 100
    allow_barge_in: bool = True
    
    # Call control
    hangup_after_LLMCall: bool = False
    call_cancellation_prompt: Optional[str] = None
    call_terminate: int = 90
    
    # Engagement features
    backchanneling: bool = False
    backchanneling_message_gap: int = 5
    backchanneling_start_delay: int = 5
    use_fillers: bool = True
    
    # Ambient effects
    ambient_noise: bool = False
    ambient_noise_track: str = "convention_hall"
    
    # User presence detection
    check_if_user_online: bool = True
    trigger_user_online_message_after: int = 10
    check_user_online_message: str = "Hey, are you still there?"
    
    # Transcription
    generate_precise_transcript: bool = False
    
    # DTMF (keypad) support
    dtmf_enabled: bool = False
    
    # Smart transfer
    enable_smart_transfer: bool = True
    transfer_number: Optional[str] = None
    max_unknown_before_transfer: int = 2
    
    # Context tracking
    enable_context_tracking: bool = True
    max_context_turns: int = 20
    
    model_config = ConfigDict(extra="allow")

    @field_validator('hangup_after_silence', mode='before')
    def set_hangup_default(cls, v):
        return v if v is not None else 20


# ==================== TASK ====================

class Task(BaseModel):
    """Task configuration."""
    tools_config: ToolsConfig
    toolchain: ToolsChainModel
    task_type: str = "conversation"
    task_config: ConversationConfig = Field(default_factory=ConversationConfig)
    
    model_config = ConfigDict(extra="allow")


# ==================== AGENT MODEL ====================

class AgentModel(BaseModel):
    """Complete agent model."""
    agent_name: str
    agent_type: str = "other"
    tasks: List[Task]
    agent_welcome_message: str = AGENT_WELCOME_MESSAGE
    
    # Metadata
    description: Optional[str] = None
    version: str = "1.0.0"
    created_at: Optional[datetime] = None
    
    # Knowledge base
    knowledge_base_id: Optional[str] = None
    
    # Billing
    account_id: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


# ==================== BILLING MODELS ====================

class BillingAccount(BaseModel):
    """Billing account model."""
    account_id: str
    balance: Decimal = Decimal("0.00")
    auto_topup_enabled: bool = False
    auto_topup_amount: Decimal = Decimal("20.00")
    auto_topup_threshold: Decimal = Decimal("5.00")
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(extra="allow")


class UsageRecord(BaseModel):
    """Usage tracking record."""
    record_id: str
    account_id: str
    service_type: str  # stt, tts, llm, telephony
    provider: str
    units: float  # minutes, characters, tokens
    cost: Decimal
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}
    
    model_config = ConfigDict(extra="allow")


class CallRecord(BaseModel):
    """Call record for billing."""
    call_sid: str
    account_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0
    total_cost: Decimal = Decimal("0.00")
    status: str = "in_progress"
    
    # Cost breakdown
    stt_cost: Decimal = Decimal("0.00")
    llm_cost: Decimal = Decimal("0.00")
    tts_cost: Decimal = Decimal("0.00")
    telephony_cost: Decimal = Decimal("0.00")
    platform_fee: Decimal = Decimal("0.00")
    
    model_config = ConfigDict(extra="allow")


# ==================== API KEY MODEL ====================

class APIKey(BaseModel):
    """API key model."""
    key_id: str
    account_id: str
    key_hash: str
    name: str = "Default Key"
    permissions: List[str] = ["all"]
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    rate_limit: int = 60  # per minute
    
    model_config = ConfigDict(extra="allow")


# ==================== WEBHOOK MODELS ====================

class WebhookConfig(BaseModel):
    """Webhook configuration."""
    url: str
    events: List[str] = ["call.started", "call.ended"]
    headers: Dict[str, str] = {}
    retry_count: int = 3
    timeout_seconds: int = 10
    
    model_config = ConfigDict(extra="allow")


class WebhookEvent(BaseModel):
    """Webhook event payload."""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = {}
    
    model_config = ConfigDict(extra="allow")


# ==================== RESPONSE MODELS ====================

class AgentResponse(BaseModel):
    """Standard agent response."""
    text: str
    action: Optional[str] = None
    data: Dict[str, Any] = {}
    confidence: float = 1.0
    should_transfer: bool = False
    transfer_reason: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class APIResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


# ==================== SERVER API MODELS ====================

class CreateAgentRequest(BaseModel):
    """Request to create/update an agent via API."""
    agent_config: AgentModel
    agent_prompts: Dict[str, Any] = {}
    
    model_config = ConfigDict(extra="allow")


class AgentApiResponse(BaseModel):
    """API response for agent operations."""
    agent_id: str
    state: str  # created, updated, deleted
    message: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


# Alias for backwards compatibility with server.py
AgentResponse = AgentApiResponse

