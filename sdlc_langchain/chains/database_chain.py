from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class DatabaseChain(BaseSDLCChain):
    """Chain for database design."""
    
    @property
    def stage_name(self) -> str:
        return "database"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["database"]
    
    def design_database(
        self,
        project_context: str,
        architecture_summary: str,
        data_requirements: str
    ) -> str:
        """Design database schema."""
        return self.invoke({
            "project_context": project_context,
            "architecture_summary": architecture_summary,
            "data_requirements": data_requirements,
        })
