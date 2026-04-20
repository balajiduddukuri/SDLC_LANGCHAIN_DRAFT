from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class RequirementsChain(BaseSDLCChain):
    """Chain for requirements gathering and analysis."""
    
    @property
    def stage_name(self) -> str:
        return "requirements"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["requirements"]
    
    def extract_requirements(self, project_context: str, business_requirements: str) -> str:
        """Extract requirements from project context."""
        return self.invoke({
            "project_context": project_context,
            "business_requirements": business_requirements,
        })
    
    def generate_user_stories(
        self, 
        project_context: str, 
        feature_name: str, 
        feature_description: str
    ) -> str:
        """Generate user stories for a feature."""
        prompts = self.get_prompts()
        chain = prompts["user_stories"] | self.provider.llm | self.output_parser
        
        return chain.invoke({
            "project_context": project_context,
            "feature_name": feature_name,
            "feature_description": feature_description,
        })
