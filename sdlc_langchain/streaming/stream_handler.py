from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses."""
    
    def __init__(
        self,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        self.on_token = on_token
        self.on_complete = on_complete
        self.on_error = on_error
        
        self._tokens: List[str] = []
        self._start_time: Optional[datetime] = None
        self._token_count = 0
        self._is_streaming = False
    
    def on_llm_start(
        self, 
        serialized: Dict[str, Any], 
        prompts: List[str], 
        **kwargs
    ):
        """Called when LLM starts generating."""
        self._tokens = []
        self._start_time = datetime.now()
        self._token_count = 0
        self._is_streaming = True
    
    def on_llm_new_token(self, token: str, **kwargs):
        """Called for each new token."""
        self._tokens.append(token)
        self._token_count += 1
        
        if self.on_token:
            self.on_token(token)
    
    def on_llm_end(self, response: LLMResult, **kwargs):
        """Called when LLM finishes generating."""
        self._is_streaming = False
        full_response = "".join(self._tokens)
        
        if self.on_complete:
            self.on_complete(full_response)
    
    def on_llm_error(self, error: Exception, **kwargs):
        """Called on LLM error."""
        self._is_streaming = False
        
        if self.on_error:
            self.on_error(error)
    
    @property
    def current_text(self) -> str:
        """Get current accumulated text."""
        return "".join(self._tokens)
    
    @property
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self._is_streaming
    
    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second."""
        if self._start_time and self._token_count > 0:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            if elapsed > 0:
                return self._token_count / elapsed
        return 0.0


class StreamHandler:
    """Manages streaming output for SDLC stages."""
    
    def __init__(self):
        self._handlers: Dict[str, StreamingCallbackHandler] = {}
        self._output_destinations: List[Callable[[str, str], None]] = []
    
    def create_handler(
        self,
        stage_name: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
    ) -> StreamingCallbackHandler:
        """Create a streaming handler for a stage."""
        handler = StreamingCallbackHandler(
            on_token=on_token or (lambda t: self._broadcast_token(stage_name, t)),
            on_complete=on_complete,
        )
        self._handlers[stage_name] = handler
        return handler
    
    def add_output_destination(
        self, 
        callback: Callable[[str, str], None]
    ):
        """Add an output destination."""
        self._output_destinations.append(callback)
    
    def _broadcast_token(self, stage_name: str, token: str):
        """Broadcast token to all destinations."""
        for destination in self._output_destinations:
            destination(stage_name, token)
    
    def get_stage_output(self, stage_name: str) -> Optional[str]:
        """Get accumulated output for a stage."""
        handler = self._handlers.get(stage_name)
        if handler:
            return handler.current_text
        return None
    
    def get_stats(self, stage_name: str) -> Dict[str, Any]:
        """Get streaming stats for a stage."""
        handler = self._handlers.get(stage_name)
        if handler:
            return {
                "tokens": handler._token_count,
                "tokens_per_second": handler.tokens_per_second,
                "is_streaming": handler.is_streaming,
            }
        return {}
