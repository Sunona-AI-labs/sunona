"""
Sunona Voice AI - Constants and Configuration

Central configuration for the entire Sunona platform.
Contains all constants, default values, and settings.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Any


# ==================== DIRECTORIES ====================

PREPROCESS_DIR = 'agent_data'
KNOWLEDGE_DIR = 'knowledge_base'
LOGS_DIR = 'logs'
RECORDINGS_DIR = 'recordings'


# ==================== PIPELINES ====================

# Default pipeline for processing (transcribe -> LLM -> synthesize)
DEFAULT_PIPELINE = ["transcriber", "llm", "synthesizer"]

# Available pipeline stages
PIPELINE_STAGES = {
    "transcriber": "Speech-to-text conversion",
    "llm": "Language model processing",
    "synthesizer": "Text-to-speech conversion",
    "output": "Send audio output",
}


# ==================== AGENT DEFAULTS ====================

# Default agent welcome message
AGENT_WELCOME_MESSAGE = "Hello! How can I help you today?"

# Default hangup after silence (seconds)
DEFAULT_HANGUP_AFTER_SILENCE = 30.0

# Response timeout (seconds)
RESPONSE_TIMEOUT = 30.0

# Maximum conversation turns before ending
MAX_CONVERSATION_TURNS = 50


# ==================== ANALYTICS ====================

HIGH_LEVEL_ASSISTANT_ANALYTICS_DATA = {
    "extraction_details": {},
    "conversation_details": {
        "total_conversations": 0,
        "finished_conversations": 0,
        "transferred_conversations": 0,
    },
    "agent_performance": {
        "successful_extractions": 0,
        "failed_extractions": 0,
        "knowledge_base_hits": 0,
        "knowledge_base_misses": 0,
        "transfers_to_human": 0,
    },
    "last_updated_at": datetime.now(timezone.utc).isoformat(),
}


# ==================== CONVERSATION CONTROL ====================

# Phrases that indicate user wants to interrupt/stop
ACCIDENTAL_INTERRUPTION_PHRASES = [
    "stop", "quit", "bye", "wait", "no", "wrong", "incorrect", "hold", "pause", "break",
    "cease", "halt", "silence", "enough", "excuse", "hold on", "hang on", "cut it",
    "that's enough", "shush", "listen", "excuse me", "hold up", "not now", "stop there",
    "stop speaking", "be quiet", "one moment", "one second", "just a sec",
]

# Phrases that indicate user wants human agent
HUMAN_TRANSFER_PHRASES = [
    "speak to human", "talk to person", "real person", "human agent",
    "manager", "supervisor", "representative", "someone else", "actual person",
    "not a robot", "live agent", "customer service", "operator",
    "speak to someone", "talk to someone", "real human", "connect me",
]

# Sensitive topics that should trigger transfer
SENSITIVE_TOPICS = [
    "refund", "complaint", "cancel subscription", "lawsuit", "legal action",
    "billing issue", "payment problem", "fraud", "scam", "sue",
    "attorney", "lawyer", "discrimination", "harassment",
]

# Frustration indicators
FRUSTRATION_INDICATORS = [
    "not helpful", "useless", "frustrated", "angry", "terrible",
    "worst service", "ridiculous", "unacceptable", "pathetic",
    "incompetent", "waste of time", "horrible",
]


# ==================== FILLER RESPONSES ====================

# Pre-function call messages (while processing)
PRE_FUNCTION_CALL_MESSAGE = {
    "en": "Just give me a moment, I'll be right back with you.",
    "es": "Dame un momento, enseguida vuelvo contigo.",
    "fr": "Un instant, je reviens tout de suite.",
    "de": "Einen Moment bitte, ich bin gleich wieder bei Ihnen.",
    "hi": "बस एक पल, मैं तुरंत वापस आता हूं।",
    "pt": "Só um momento, já volto.",
    "it": "Un momento, torno subito.",
    "ja": "少々お待ちください。すぐに戻ります。",
    "zh": "请稍等，我马上回来。",
    "ar": "لحظة من فضلك، سأعود إليك فوراً.",
}

# General filler phrases
FILLER_PHRASES = [
    "No worries.", "It's fine.", "I'm here.", "No rush.", "Take your time.",
    "Great!", "Awesome!", "Fantastic!", "Wonderful!", "Perfect!", "Excellent!",
    "I get it.", "Noted.", "Alright.", "I understand.", "Understood.", "Got it.",
    "Sure.", "Okay.", "Right.", "Absolutely.", "Sure thing.",
    "I see.", "Gotcha.", "Makes sense.", "Of course.", "Certainly.",
]

# Categorized fillers for context-aware responses
FILLER_DICT = {
    "Unsure": ["No worries.", "It's fine.", "I'm here.", "No rush.", "Take your time."],
    "Positive": ["Great!", "Awesome!", "Fantastic!", "Wonderful!", "Perfect!", "Excellent!", "Amazing!"],
    "Negative": ["I understand.", "I get it.", "I see.", "That makes sense.", "I hear you."],
    "Neutral": ["Sure.", "Okay.", "Right.", "Absolutely.", "Sure thing.", "Of course."],
    "Explaining": ["I see.", "Gotcha.", "Makes sense.", "Interesting.", "I follow."],
    "Greeting": ["Hello!", "Hi there!", "Hi!", "Hey!", "Good to hear from you!"],
    "Farewell": ["Goodbye!", "Thank you!", "Take care!", "Bye!", "Have a great day!"],
    "Thanking": ["You're welcome!", "No problem!", "Happy to help!", "Anytime!"],
    "Apology": ["I'm sorry to hear that.", "I apologize.", "My apologies.", "I'm sorry."],
    "Clarification": ["Could you clarify?", "Can you explain a bit more?", "Tell me more about that."],
    "Confirmation": ["Got it.", "Noted.", "Understood.", "I've made a note of that."],
    "Thinking": ["Let me think...", "Good question...", "Hmm...", "Let me check..."],
    "Transfer": ["Let me connect you with someone who can help.", "I'll get a specialist for you."],
}

# Processing/waiting messages
CHECKING_THE_DOCUMENTS_FILLER = "Just a moment, checking the details for you..."
THINKING_FILLER = "Let me look into that for you..."
SEARCHING_FILLER = "Searching for that information..."

# Call transfer messages
TRANSFERRING_CALL_FILLER = {
    "en": "I'll connect you with a team member who can help. One moment please...",
    "es": "Te conectaré con un miembro del equipo que puede ayudarte. Un momento por favor...",
    "fr": "Je vous mets en relation avec un membre de l'équipe. Un instant s'il vous plaît...",
    "de": "Ich verbinde Sie mit einem Teammitglied. Einen Moment bitte...",
    "hi": "मैं आपको एक टीम मेंबर से जोड़ रहा हूं। कृपया एक पल प्रतीक्षा करें...",
}

# Seamless transfer (no awkward announcement)
SEAMLESS_TRANSFER_MESSAGES = {
    "out_of_context": "Let me connect you with someone who specializes in that.",
    "customer_request": "Of course. Connecting you now.",
    "sensitive_topic": "I'll get one of our specialists to assist you directly.",
    "escalation": "I understand. Let me connect you with a colleague who can help.",
    "default": "One moment please, connecting you now.",
}


# ==================== USER PRESENCE ====================

DEFAULT_USER_ONLINE_MESSAGE = "Hey, are you still there?"
DEFAULT_USER_ONLINE_MESSAGE_TRIGGER_DURATION = 6  # seconds
USER_IDLE_REMINDER_MESSAGES = [
    "I'm still here when you're ready.",
    "Take your time, I'll wait.",
    "Just checking in - are you still there?",
    "No rush, I'm here whenever you need me.",
]


# ==================== DEFAULTS ====================

DEFAULT_LANGUAGE_CODE = 'en'
DEFAULT_TIMEZONE = 'America/Los_Angeles'
DEFAULT_VOICE_ID = 'EXAVITQu4vr4xnSDxMaL'  # ElevenLabs Sarah
DEFAULT_VOICE_SPEED = 1.0
DEFAULT_LLM_MODEL = 'gpt-4o-mini'
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 500


# Provider pricing (STILL Core API compatible)
PROVIDER_COSTS = {}

# Free models (OpenRouter)
FREE_LLM_MODELS = [
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "huggingfaceh4/zephyr-7b-beta:free",
]


# ==================== AGENT CONFIGURATION ====================

# Agent behavior
MAX_CONVERSATION_TURNS = 50
MAX_UNKNOWN_BEFORE_TRANSFER = 2
RESPONSE_TIMEOUT = 30.0
ENABLE_INTERRUPTION = True

# Agent types and their use cases
AGENT_TYPE_MAPPING = {
    "lead_capture": "extraction",
    "appointment_booking": "extraction",
    "data_collection": "extraction",
    "survey": "extraction",
    "faq": "knowledge_base",
    "customer_support": "knowledge_base",
    "ivr_menu": "graph",
    "guided_flow": "graph_conversational",
    "sales": "graph_conversational",
    "crm_integration": "webhook",
    "general_conversation": "contextual",
}

# Intent detection patterns
INTENT_PATTERNS = {
    "appointment": ["book", "appointment", "schedule", "reserve", "meeting", "consultation"],
    "lead_capture": ["interested", "demo", "pricing", "contact me", "sign up", "more information"],
    "support": ["help", "problem", "issue", "not working", "error", "broken", "fix"],
    "faq": ["what is", "how do", "where can", "when does", "explain", "tell me about"],
    "sales": ["buy", "purchase", "order", "pricing", "cost", "discount", "deal"],
}


# ==================== EXTRACTION FIELDS ====================

# Common extraction field templates
LEAD_CAPTURE_FIELDS = [
    {"name": "name", "type": "text", "required": True, "prompt": "May I have your name please?"},
    {"name": "email", "type": "email", "required": True, "prompt": "What's the best email to reach you?"},
    {"name": "phone", "type": "phone", "required": False, "prompt": "And your phone number?"},
    {"name": "company", "type": "text", "required": False, "prompt": "What company are you with?"},
]

APPOINTMENT_FIELDS = [
    {"name": "name", "type": "text", "required": True, "prompt": "May I have your name for the appointment?"},
    {"name": "date", "type": "date", "required": True, "prompt": "What date works best for you?"},
    {"name": "time", "type": "time", "required": True, "prompt": "And what time would you prefer?"},
    {"name": "phone", "type": "phone", "required": True, "prompt": "What phone number should we confirm with?"},
]

SURVEY_FIELDS = [
    {"name": "rating", "type": "number", "required": True, "prompt": "On a scale of 1-10, how was your experience?"},
    {"name": "feedback", "type": "text", "required": False, "prompt": "Any additional feedback you'd like to share?"},
]


# ==================== KNOWLEDGE BASE ====================

# Website scraping limits
MAX_PAGES_TO_SCRAPE = 50
SCRAPE_DELAY_SECONDS = 0.5
MAX_CONTENT_PER_PAGE = 10000  # characters

# Chunk settings for RAG
CHUNK_SIZE = 1000  # words
CHUNK_OVERLAP = 100  # words


# ==================== VOICE SETTINGS ====================

# Voice Activity Detection
VAD_THRESHOLD = 0.5
VAD_MIN_SILENCE_MS = 300
VAD_SPEECH_PAD_MS = 100

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "pcm"


# ==================== API SETTINGS ====================

# API key settings
API_KEY_PREFIX = "sk_"
API_KEY_LENGTH = 32
SESSION_TOKEN_EXPIRY_HOURS = 24
RATE_LIMIT_PER_MINUTE = 60

# Webhook settings
WEBHOOK_RETRY_COUNT = 3
WEBHOOK_TIMEOUT_SECONDS = 10


# ==================== SYSTEM PROMPTS ====================

DEFAULT_SYSTEM_PROMPT = """You are a helpful AI voice assistant. Be conversational, friendly, and professional.

GUIDELINES:
1. Keep responses concise (1-3 sentences) - this is a phone call
2. Be natural and conversational
3. If you don't know something, honestly say so
4. Offer to connect with a human if you can't help
5. Be empathetic and understanding
"""

CUSTOMER_SUPPORT_PROMPT = """You are a customer support AI assistant. Be helpful, empathetic, and solution-oriented.

GUIDELINES:
1. Acknowledge the customer's issue
2. Ask clarifying questions if needed
3. Provide clear, actionable solutions
4. If you can't resolve, offer to connect with a specialist
5. Stay calm and patient even if the customer is frustrated
"""

SALES_AGENT_PROMPT = """You are a friendly sales AI assistant. Be helpful without being pushy.

GUIDELINES:
1. Understand the customer's needs first
2. Present relevant products/services
3. Answer questions honestly
4. Don't pressure - guide gently
5. Offer to connect with a sales specialist for complex questions
"""

APPOINTMENT_PROMPT = """You are an appointment booking AI assistant. Be efficient and friendly.

GUIDELINES:
1. Collect the required information (name, date, time, contact)
2. Confirm details before finalizing
3. Be flexible with scheduling
4. Offer alternatives if preferred time isn't available
"""


# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    "insufficient_balance": "Your account balance is low. Please top up to continue using premium features.",
    "api_key_invalid": "Invalid API key. Please check your credentials.",
    "rate_limit_exceeded": "Too many requests. Please try again later.",
    "service_unavailable": "Service temporarily unavailable. Please try again.",
    "llm_error": "I'm having trouble processing that. Could you repeat?",
    "transcription_error": "I didn't catch that. Could you say that again?",
    "unknown_error": "Something went wrong. Please try again.",
}


# ==================== SUCCESS MESSAGES ====================

SUCCESS_MESSAGES = {
    "call_started": "Call connected successfully.",
    "data_extracted": "Got it! I've recorded your information.",
    "appointment_booked": "Your appointment has been booked.",
    "transfer_initiated": "Connecting you with a specialist now.",
    "feedback_received": "Thank you for your feedback!",
}


# ==================== VERSION INFO ====================

VERSION = "1.0.0"
API_VERSION = "v1"
BUILD_DATE = "2024-12-28"
