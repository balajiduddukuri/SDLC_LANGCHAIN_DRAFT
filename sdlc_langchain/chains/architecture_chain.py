from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class ArchitectureChain(BaseSDLCChain):
    """Chain for architecture design."""
    
    @property
    def stage_name(self) -> str:
        return "architecture"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["architecture"]
    
    def design_architecture(self, project_context: str, requirements_summary: str) -> str:
        """Design high-level architecture."""
        return self.invoke({
            "project_context": project_context,
            "requirements_summary": requirements_summary,
        })
