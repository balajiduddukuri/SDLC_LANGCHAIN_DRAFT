from typing import Optional, Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel

from .base_provider import BaseLLMProvider
from config import llm_config


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI LLM Provider."""
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        streaming: bool = True,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
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
        self.api_key = api_key or llm_config.azure_api_key
        self.azure_endpoint = azure_endpoint or llm_config.azure_endpoint
        self.azure_deployment = azure_deployment or llm_config.azure_deployment
        self.api_version = api_version
    
    def _create_llm(self) -> BaseChatModel:
        """Create Azure OpenAI ChatModel instance."""
        return AzureChatOpenAI(
            azure_deployment=self.azure_deployment,
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=self.streaming,
            callbacks=self.callbacks,
            **self.extra_config
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Azure OpenAI model information."""
        return {
            "provider": "Azure OpenAI",
            "model": self.model_name,
            "deployment": self.azure_deployment,
            "supports_streaming": True,
        }
    
    def validate_config(self) -> bool:
        """Validate Azure OpenAI configuration."""
        if not self.api_key:
            raise ValueError("Azure OpenAI API key is required")
        if not self.azure_endpoint:
            raise ValueError("Azure OpenAI endpoint is required")
        if not self.azure_deployment:
            raise ValueError("Azure OpenAI deployment name is required")
        return True
