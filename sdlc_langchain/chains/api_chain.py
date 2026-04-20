from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class APIChain(BaseSDLCChain):
    """Chain for API design."""
    
    @property
    def stage_name(self) -> str:
        return "api"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["api"]
    
    def design_api(
        self,
        project_context: str,
        architecture_summary: str,
        service_name: str
    ) -> str:
        """Design API for a service."""
        return self.invoke({
            "project_context": project_context,
            "architecture_summary": architecture_summary,
            "service_name": service_name,
        })
