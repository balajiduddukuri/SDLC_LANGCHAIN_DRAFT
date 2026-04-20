from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel

from .base_provider import BaseLLMProvider
from config import llm_config


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM Provider."""
    
    def __init__(
        self,
        model_name: str = "gpt-4-turbo-preview",
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
        self.api_key = api_key or llm_config.openai_api_key
    
    def _create_llm(self) -> BaseChatModel:
        """Create OpenAI ChatModel instance."""
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=self.streaming,
            api_key=self.api_key,
            callbacks=self.callbacks,
            **self.extra_config
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        model_limits = {
            "gpt-4-turbo-preview": {"context": 128000, "output": 4096},
            "gpt-4": {"context": 8192, "output": 8192},
            "gpt-4-32k": {"context": 32768, "output": 32768},
            "gpt-3.5-turbo": {"context": 16385, "output": 4096},
        }
        
        limits = model_limits.get(
            self.model_name, 
            {"context": 8192, "output": 4096}
        )
        
        return {
            "provider": "OpenAI",
            "model": self.model_name,
            "context_window": limits["context"],
            "max_output_tokens": limits["output"],
            "supports_streaming": True,
            "supports_functions": True,
        }
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        return True
