from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class SecurityChain(BaseSDLCChain):
    """Chain for security design."""
    
    @property
    def stage_name(self) -> str:
        return "security"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["security"]
    
    def design_security(
        self,
        project_context: str,
        architecture_summary: str,
        compliance_requirements: str
    ) -> str:
        """Design security architecture."""
        return self.invoke({
            "project_context": project_context,
            "architecture_summary": architecture_summary,
            "compliance_requirements": compliance_requirements,
        })
