from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser

from providers.base_provider import BaseLLMProvider
from providers.provider_factory import LLMProviderFactory
from memory.conversation_memory import ConversationMemoryManager
from memory.project_memory import ProjectMemory
from streaming.stream_handler import StreamingCallbackHandler, StreamHandler
from config import streaming_config


class BaseSDLCChain(ABC):
    """Base class for all SDLC chains."""
    
    def __init__(
        self,
        provider: BaseLLMProvider = None,
        conversation_memory: ConversationMemoryManager = None,
        project_memory: ProjectMemory = None,
        enable_streaming: bool = True,
    ):
        self.provider = provider or LLMProviderFactory.create_from_config()
        self.conversation_memory = conversation_memory
        self.project_memory = project_memory
        self.enable_streaming = enable_streaming and streaming_config.enabled
        
        self.output_parser = StrOutputParser()
        self.stream_handler = StreamHandler() if self.enable_streaming else None
        
        self._execution_stats: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Return the name of this SDLC stage."""
        pass
    
    @abstractmethod
    def get_prompts(self) -> Dict[str, Any]:
        """Return the prompts for this stage."""
        pass
    
    def _build_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build context including memory."""
        context = input_data.copy()
        
        if self.project_memory:
            context["previous_stages"] = self.project_memory.get_dependent_outputs(
                self.stage_name
            )
        
        if self.conversation_memory:
            context["conversation_history"] = self.conversation_memory.to_context_string(
                max_length=2000
            )
        
        return context
    
    def invoke(self, input_data: Dict[str, Any]) -> str:
        """Synchronously invoke the chain."""
        start_time = datetime.now()
        
        context = self._build_context(input_data)
        prompts = self.get_prompts()
        main_prompt = prompts.get("main") or list(prompts.values())[0]
        
        chain = main_prompt | self.provider.llm | self.output_parser
        
        if self.enable_streaming and self.stream_handler:
            callback = self.stream_handler.create_handler(self.stage_name)
            result = chain.invoke(context, config={"callbacks": [callback]})
        else:
            result = chain.invoke(context)
        
        self._on_completion(result, start_time)
        self._store_result(input_data, result)
        
        return result
    
    def _on_completion(self, result: str, start_time: datetime):
        """Handle completion of generation."""
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        self._execution_stats = {
            "stage": self.stage_name,
            "execution_time_seconds": execution_time,
            "output_length": len(result),
            "estimated_tokens": len(result) // 4,
        }
    
    def _store_result(self, input_data: Dict[str, Any], result: str):
        """Store result in memory systems."""
        if self.project_memory:
            self.project_memory.store_stage_output(
                self.stage_name,
                result,
                tokens_used=self._execution_stats.get("estimated_tokens", 0),
                execution_time=self._execution_stats.get("execution_time_seconds", 0),
            )
        
        if self.conversation_memory:
            self.conversation_memory.add_interaction(
                stage=self.stage_name,
                human_input=str(input_data)[:500],
                ai_output=result[:1000],
                metadata=self._execution_stats,
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self._execution_stats.copy()
