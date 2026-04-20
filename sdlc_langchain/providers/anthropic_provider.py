from typing import Optional, Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel

from .base_provider import BaseLLMProvider
from config import llm_config


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM Provider."""
    
    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        streaming: bool = True,
        api_key: Optional[str] = None,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            callbacks=callbacks,
            **kwargs
        )
        self.api_key = api_key or llm_config.anthropic_api_key
    
    def _create_llm(self) -> BaseChatModel:
        """Create Anthropic ChatModel instance."""
        return ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=self.streaming,
            api_key=self.api_key,
            callbacks=self.callbacks,
            **self.extra_config
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information."""
        return {
            "provider": "Anthropic",
            "model": self.model_name,
            "context_window": 200000,
            "max_output_tokens": 4096,
            "supports_streaming": True,
        }
    
    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        return True
