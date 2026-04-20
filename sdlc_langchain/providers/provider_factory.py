from typing import Optional, List
from langchain_core.callbacks import BaseCallbackHandler

from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .azure_provider import AzureOpenAIProvider
from .ollama_provider import OllamaProvider
from config import LLMProvider, llm_config


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.AZURE_OPENAI: AzureOpenAIProvider,
        LLMProvider.OLLAMA: OllamaProvider,
    }
    
    _default_models = {
        LLMProvider.OPENAI: "gpt-4-turbo-preview",
        LLMProvider.ANTHROPIC: "claude-3-opus-20240229",
        LLMProvider.AZURE_OPENAI: "gpt-4",
        LLMProvider.OLLAMA: "llama2",
    }
    
    @classmethod
    def create(
        cls,
        provider: Optional[LLMProvider] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        streaming: bool = True,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """Create an LLM provider instance."""
        provider = provider or llm_config.provider
        model_name = model_name or llm_config.model_name or cls._default_models.get(provider)
        
        if provider not in cls._providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_class = cls._providers[provider]
        
        return provider_class(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            callbacks=callbacks,
            **kwargs
        )
    
    @classmethod
    def create_from_config(
        cls,
        callbacks: Optional[List[BaseCallbackHandler]] = None
    ) -> BaseLLMProvider:
        """Create provider from global configuration."""
        return cls.create(
            provider=llm_config.provider,
            model_name=llm_config.model_name,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens,
            streaming=llm_config.streaming,
            callbacks=callbacks,
        )
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List available providers."""
        return [p.value for p in cls._providers.keys()]
