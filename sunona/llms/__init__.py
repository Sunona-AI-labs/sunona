"""
Sunona Voice AI - LLM Module

Large Language Model providers for conversation processing.

Providers:
- openai: Direct OpenAI API (GPT-4o, GPT-4o-mini)
- openrouter: OpenRouter API (Mistral, Llama, Gemma free models)
- litellm: Universal provider (100+ models including Anthropic, Azure, Groq)
- azure: Azure OpenAI
- groq: Groq (ultra-fast inference)
- anthropic: Anthropic Claude
- together: Together AI
- fireworks: Fireworks AI
- deepseek: DeepSeek
- mistral: Mistral AI
- cohere: Cohere
- perplexity: Perplexity AI
- ollama: Local Ollama
"""

from sunona.llms.base_llm import BaseLLM

# Lazy imports to avoid unnecessary dependencies
def _get_openrouter_llm():
    from sunona.llms.openrouter_llm import OpenRouterLLM
    return OpenRouterLLM

def _get_openai_llm():
    from sunona.llms.openai_llm import OpenAILLM
    return OpenAILLM

def _get_litellm_provider():
    from sunona.llms.litellm_llm import LiteLLMProvider
    return LiteLLMProvider


# Build exports for providers.py compatibility
OpenRouterLLM = _get_openrouter_llm()
OpenAiLLM = _get_openai_llm()
LiteLLM = _get_litellm_provider()


# Azure LLM wrapper (uses LiteLLM with azure prefix)
class AzureLLM(LiteLLM):
    """Azure OpenAI LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "azure/gpt-4")
        if not model.startswith("azure/"):
            model = f"azure/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


# Provider-specific LLM classes for convenience
class GroqLLM(LiteLLM):
    """Groq LLM wrapper - Ultra-fast inference."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "groq/llama-3.1-70b-versatile")
        if not model.startswith("groq/"):
            model = f"groq/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class AnthropicLLM(LiteLLM):
    """Anthropic Claude LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "claude-3-5-sonnet-20241022")
        kwargs["model"] = model
        super().__init__(**kwargs)


class TogetherLLM(LiteLLM):
    """Together AI LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "together_ai/meta-llama/Llama-3-70b-chat-hf")
        if not model.startswith("together"):
            model = f"together_ai/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class FireworksLLM(LiteLLM):
    """Fireworks AI LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "fireworks_ai/accounts/fireworks/models/llama-v3-70b-instruct")
        if not model.startswith("fireworks"):
            model = f"fireworks_ai/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class DeepSeekLLM(LiteLLM):
    """DeepSeek LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "deepseek/deepseek-chat")
        if not model.startswith("deepseek/"):
            model = f"deepseek/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class MistralLLM(LiteLLM):
    """Mistral AI LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "mistral/mistral-large-latest")
        if not model.startswith("mistral/"):
            model = f"mistral/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class CohereLLM(LiteLLM):
    """Cohere LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "cohere/command-r-plus")
        if not model.startswith("cohere/"):
            model = f"cohere/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class PerplexityLLM(LiteLLM):
    """Perplexity AI LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "perplexity/llama-3.1-sonar-large-128k-online")
        if not model.startswith("perplexity/"):
            model = f"perplexity/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class OllamaLLM(LiteLLM):
    """Ollama (local) LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "ollama/llama3")
        if not model.startswith("ollama/"):
            model = f"ollama/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class DeepInfraLLM(LiteLLM):
    """DeepInfra LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "deepinfra/meta-llama/Llama-2-70b-chat-hf")
        if not model.startswith("deepinfra/"):
            model = f"deepinfra/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class AnyscaleLLM(LiteLLM):
    """Anyscale LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "anyscale/meta-llama/Llama-2-70b-chat-hf")
        if not model.startswith("anyscale/"):
            model = f"anyscale/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class VllmLLM(LiteLLM):
    """vLLM LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "vllm/meta-llama/Llama-2-70b-chat-hf")
        if not model.startswith("vllm/"):
            model = f"vllm/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class GoogleLLM(LiteLLM):
    """Google/Gemini LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "gemini/gemini-1.5-flash")
        if not model.startswith("gemini/"):
            model = f"gemini/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


class BedrockLLM(LiteLLM):
    """AWS Bedrock LLM wrapper."""
    def __init__(self, **kwargs):
        model = kwargs.get("model", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0")
        if not model.startswith("bedrock/"):
            model = f"bedrock/{model}"
        kwargs["model"] = model
        super().__init__(**kwargs)


__all__ = [
    # Base
    "BaseLLM",
    
    # Primary providers
    "OpenAiLLM",
    "OpenRouterLLM",
    "LiteLLM",
    "AzureLLM",
    
    # Provider-specific wrappers
    "GroqLLM",
    "AnthropicLLM",
    "TogetherLLM",
    "FireworksLLM",
    "DeepSeekLLM",
    "MistralLLM",
    "CohereLLM",
    "PerplexityLLM",
    "OllamaLLM",
    "DeepInfraLLM",
    "AnyscaleLLM",
    "VllmLLM",
    "GoogleLLM",
    "BedrockLLM",
    
    # Factory
    "create_llm",
]


# Provider mapping for create_llm factory
PROVIDER_CLASSES = {
    # Direct OpenAI compatible
    "openai": OpenAiLLM,
    "custom": OpenAiLLM,
    "ola": OpenAiLLM,
    
    # OpenRouter
    "openrouter": OpenRouterLLM,
    
    # Azure
    "azure": AzureLLM,
    "azure-openai": AzureLLM,
    
    # Provider-specific wrappers
    "groq": GroqLLM,
    "anthropic": AnthropicLLM,
    "together": TogetherLLM,
    "fireworks": FireworksLLM,
    "deepseek": DeepSeekLLM,
    "mistral": MistralLLM,
    "cohere": CohereLLM,
    "perplexity": PerplexityLLM,
    "ollama": OllamaLLM,
    "deepinfra": DeepInfraLLM,
    "anyscale": AnyscaleLLM,
    "vllm": VllmLLM,
    "google": GoogleLLM,
    "gemini": GoogleLLM,
    "bedrock": BedrockLLM,
    "vertex": GoogleLLM,
    "replicate": LiteLLM,
    "huggingface": LiteLLM,
    
    # Generic LiteLLM
    "litellm": LiteLLM,
}


def create_llm(provider: str, **kwargs) -> BaseLLM:
    """
    Factory function to create an LLM instance.
    
    Args:
        provider: The LLM provider name
            - 'openai': Direct OpenAI API
            - 'openrouter': OpenRouter API (free models)
            - 'azure': Azure OpenAI
            - 'groq': Groq (ultra-fast)
            - 'anthropic': Anthropic Claude
            - 'together': Together AI
            - 'fireworks': Fireworks AI
            - 'deepseek': DeepSeek
            - 'mistral': Mistral AI
            - 'cohere': Cohere
            - 'perplexity': Perplexity AI
            - 'ollama': Local Ollama
            - 'google': Google Gemini
            - 'bedrock': AWS Bedrock
            - 'litellm': Universal provider
        **kwargs: Provider-specific configuration
        
    Returns:
        BaseLLM: An LLM instance
        
    Raises:
        ValueError: If provider is not supported
    """
    provider_lower = provider.lower()
    
    if provider_lower in PROVIDER_CLASSES:
        return PROVIDER_CLASSES[provider_lower](**kwargs)
    
    raise ValueError(
        f"Unsupported LLM provider: '{provider}'. "
        f"Available: {list(PROVIDER_CLASSES.keys())}"
    )
