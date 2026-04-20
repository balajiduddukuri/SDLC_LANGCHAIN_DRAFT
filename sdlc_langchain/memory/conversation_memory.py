from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from config import MemoryType, memory_config


class ConversationEntry(BaseModel):
    """Single conversation entry."""
    timestamp: datetime
    stage: str
    input_summary: str
    output_summary: str
    tokens_used: int = 0
    metadata: Dict[str, Any] = {}


class ConversationMemoryManager:
    """Manages conversation history across SDLC stages."""
    
    def __init__(
        self,
        project_id: str,
        memory_type: MemoryType = None,
        llm=None,
    ):
        self.project_id = project_id
        self.memory_type = memory_type or memory_config.type
        self.llm = llm
        
        self._memories: Dict[str, Any] = {}
        self._conversation_history: List[ConversationEntry] = []
        self._stage_contexts: Dict[str, str] = {}
        
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize the memory system."""
        self._memories["main"] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )
    
    def get_memory(self, stage: Optional[str] = None):
        """Get memory for a specific stage or main memory."""
        if stage and stage in self._memories:
            return self._memories[stage]
        return self._memories.get("main")
    
    def add_interaction(
        self,
        stage: str,
        human_input: str,
        ai_output: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add an interaction to memory."""
        main_memory = self.get_memory()
        if main_memory:
            main_memory.save_context(
                {"input": f"[{stage}] {human_input[:500]}..."},
                {"output": ai_output[:1000] + "..." if len(ai_output) > 1000 else ai_output}
            )
        
        entry = ConversationEntry(
            timestamp=datetime.now(),
            stage=stage,
            input_summary=human_input[:200],
            output_summary=ai_output[:500],
            metadata=metadata or {},
        )
        self._conversation_history.append(entry)
        self._stage_contexts[stage] = ai_output
    
    def get_stage_context(self, stage: str) -> Optional[str]:
        """Get the output context from a specific stage."""
        return self._stage_contexts.get(stage)
    
    def get_previous_stages_context(self, current_stage: str) -> str:
        """Get summarized context from all previous stages."""
        context_parts = []
        
        stage_order = [
            "requirements", "architecture", "database", "api",
            "security", "implementation", "testing", "devops",
            "monitoring", "documentation"
        ]
        
        try:
            current_idx = stage_order.index(current_stage)
        except ValueError:
            current_idx = len(stage_order)
        
        for stage in stage_order[:current_idx]:
            if stage in self._stage_contexts:
                summary = self._stage_contexts[stage][:500]
                context_parts.append(f"### {stage.upper()} Summary:\n{summary}...")
        
        return "\n\n".join(context_parts)
    
    def get_conversation_history(self) -> List[ConversationEntry]:
        """Get full conversation history."""
        return self._conversation_history
    
    def get_messages(self) -> List[BaseMessage]:
        """Get messages from memory."""
        main_memory = self.get_memory()
        if main_memory and hasattr(main_memory, 'chat_memory'):
            return main_memory.chat_memory.messages
        return []
    
    def clear(self, stage: Optional[str] = None):
        """Clear memory."""
        if stage and stage in self._memories:
            self._memories[stage].clear()
        elif not stage:
            for memory in self._memories.values():
                if hasattr(memory, 'clear'):
                    memory.clear()
            self._conversation_history.clear()
            self._stage_contexts.clear()
    
    def export_history(self) -> Dict[str, Any]:
        """Export conversation history as dictionary."""
        return {
            "project_id": self.project_id,
            "memory_type": self.memory_type.value,
            "stages": list(self._stage_contexts.keys()),
            "history": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "stage": entry.stage,
                    "input_summary": entry.input_summary,
                    "output_summary": entry.output_summary,
                }
                for entry in self._conversation_history
            ],
        }
    
    def to_context_string(self, max_length: int = 4000) -> str:
        """Convert memory to context string for prompts."""
        messages = self.get_messages()
        context_parts = []
        current_length = 0
        
        for msg in reversed(messages):
            msg_text = f"{msg.type}: {msg.content[:500]}"
            if current_length + len(msg_text) > max_length:
                break
            context_parts.insert(0, msg_text)
            current_length += len(msg_text)
        
        return "\n".join(context_parts)
