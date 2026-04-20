from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Dict, Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage, AIMessage


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        streaming: bool = True,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
        **kwargs
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.callbacks = callbacks or []
        self.extra_config = kwargs
        self._llm: Optional[BaseChatModel] = None
    
    @abstractmethod
    def _create_llm(self) -> BaseChatModel:
        """Create and return the LLM instance."""
        pass
    
    @property
    def llm(self) -> BaseChatModel:
        """Get or create the LLM instance."""
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm
    
    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Synchronously invoke the LLM."""
        return self.llm.invoke(messages, **kwargs)
    
    async def ainvoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Asynchronously invoke the LLM."""
        return await self.llm.ainvoke(messages, **kwargs)
    
    async def astream(
        self, 
        messages: List[BaseMessage], 
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream responses asynchronously."""
        async for chunk in self.llm.astream(messages, **kwargs):
            if hasattr(chunk, 'content'):
                yield chunk.content
    
    def add_callback(self, callback: BaseCallbackHandler):
        """Add a callback handler."""
        self.callbacks.append(callback)
        self._llm = None
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in text."""
        return len(text) // 4
    
    def validate_config(self) -> bool:
        """Validate the provider configuration."""
        return True
