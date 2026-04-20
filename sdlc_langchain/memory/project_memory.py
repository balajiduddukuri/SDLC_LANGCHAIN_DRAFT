from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from pydantic import BaseModel, Field

from models.project_context import ProjectContext


class StageOutput(BaseModel):
    """Output from an SDLC stage."""
    stage_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: int = 1
    tokens_used: int = 0
    execution_time_seconds: float = 0
    checksum: str = ""
    
    def compute_checksum(self):
        """Compute content checksum."""
        self.checksum = hashlib.md5(self.content.encode()).hexdigest()[:8]


class ProjectMemory:
    """Manages project-level memory across SDLC stages."""
    
    def __init__(self, project_context: ProjectContext):
        self.project_context = project_context
        self.project_id = self._generate_project_id()
        
        self._stage_outputs: Dict[str, StageOutput] = {}
        self._stage_versions: Dict[str, List[StageOutput]] = {}
        self._artifacts: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "project_name": project_context.project_name,
        }
    
    def _generate_project_id(self) -> str:
        """Generate unique project ID."""
        content = f"{self.project_context.project_name}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def store_stage_output(
        self,
        stage_name: str,
        content: str,
        tokens_used: int = 0,
        execution_time: float = 0,
    ):
        """Store output from a stage."""
        output = StageOutput(
            stage_name=stage_name,
            content=content,
            tokens_used=tokens_used,
            execution_time_seconds=execution_time,
        )
        output.compute_checksum()
        
        if stage_name in self._stage_outputs:
            if stage_name not in self._stage_versions:
                self._stage_versions[stage_name] = []
            self._stage_versions[stage_name].append(self._stage_outputs[stage_name])
        
        self._stage_outputs[stage_name] = output
    
    def get_stage_output(self, stage_name: str) -> Optional[str]:
        """Get output from a stage."""
        if stage_name in self._stage_outputs:
            return self._stage_outputs[stage_name].content
        return None
    
    def get_stage_summary(self, stage_name: str, max_length: int = 500) -> str:
        """Get summarized output from a stage."""
        content = self.get_stage_output(stage_name)
        if content:
            return content[:max_length] + "..." if len(content) > max_length else content
        return ""
    
    def get_dependent_outputs(self, stage_name: str) -> Dict[str, str]:
        """Get outputs from dependent stages."""
        dependencies = {
            "architecture": ["requirements"],
            "database": ["architecture", "requirements"],
            "api": ["architecture", "database"],
            "security": ["architecture", "api"],
            "implementation": ["architecture", "database", "api", "security"],
            "testing": ["requirements", "implementation"],
            "devops": ["architecture", "implementation"],
            "monitoring": ["architecture", "devops"],
            "documentation": ["implementation", "testing", "devops"],
        }
        
        required_stages = dependencies.get(stage_name, [])
        return {
            stage: self.get_stage_summary(stage)
            for stage in required_stages
            if self.get_stage_output(stage)
        }
    
    def build_context_for_stage(self, stage_name: str) -> str:
        """Build full context string for a stage."""
        parts = [
            "## PROJECT CONTEXT",
            self.project_context.to_context_string(),
            "",
            "## PREVIOUS STAGE OUTPUTS",
        ]
        
        dependent_outputs = self.get_dependent_outputs(stage_name)
        for dep_stage, output in dependent_outputs.items():
            parts.append(f"### {dep_stage.upper()}")
            parts.append(output)
            parts.append("")
        
        return "\n".join(parts)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total_tokens = sum(
            output.tokens_used 
            for output in self._stage_outputs.values()
        )
        total_time = sum(
            output.execution_time_seconds 
            for output in self._stage_outputs.values()
        )
        
        return {
            "project_id": self.project_id,
            "stages_completed": len(self._stage_outputs),
            "total_tokens_used": total_tokens,
            "total_execution_time_seconds": total_time,
        }
    
    def export(self) -> Dict[str, Any]:
        """Export complete project memory."""
        return {
            "project_id": self.project_id,
            "metadata": self._metadata,
            "project_context": self.project_context.model_dump(),
            "stages": {
                name: {
                    "content": output.content,
                    "timestamp": output.timestamp.isoformat(),
                    "checksum": output.checksum,
                }
                for name, output in self._stage_outputs.items()
            },
            "stats": self.get_execution_stats(),
        }
