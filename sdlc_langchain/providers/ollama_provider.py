from typing import Optional, Dict, Any, List
from langchain_community.chat_models import ChatOllama
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel

from .base_provider import BaseLLMProvider
from config import llm_config


class OllamaProvider(BaseLLMProvider):
    """Ollama Local LLM Provider."""
    
    def __init__(
        self,
        model_name: str = "llama2",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        streaming: bool = True,
        base_url: Optional[str] = None,
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
        self.base_url = base_url or llm_config.ollama_base_url
    
    def _create_llm(self) -> BaseChatModel:
        """Create Ollama ChatModel instance."""
        return ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            num_predict=self.max_tokens,
            base_url=self.base_url,
            callbacks=self.callbacks,
            **self.extra_config
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information."""
        return {
            "provider": "Ollama",
            "model": self.model_name,
            "base_url": self.base_url,
            "supports_streaming": True,
            "local": True,
        }
    
    def validate_config(self) -> bool:
        """Validate Ollama configuration."""
        return True
