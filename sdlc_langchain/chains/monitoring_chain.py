from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class MonitoringChain(BaseSDLCChain):
    """Chain for monitoring and observability design."""
    
    @property
    def stage_name(self) -> str:
        return "monitoring"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["monitoring"]
    
    def design_observability(
        self,
        project_context: str,
        architecture_summary: str,
        sla_requirements: str = "99.9% availability"
    ) -> str:
        """Design observability strategy."""
        return self.invoke({
            "project_context": project_context,
            "architecture_summary": architecture_summary,
            "sla_requirements": sla_requirements,
        })
