from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class DocumentationChain(BaseSDLCChain):
    """Chain for documentation generation."""
    
    @property
    def stage_name(self) -> str:
        return "documentation"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["documentation"]
    
    def generate_technical_docs(
        self,
        component_name: str,
        component_purpose: str,
        technical_details: str
    ) -> str:
        """Generate technical documentation."""
        prompts = self.get_prompts()
        chain = prompts["technical"] | self.provider.llm | self.output_parser
        
        return chain.invoke({
            "component_name": component_name,
            "component_purpose": component_purpose,
            "technical_details": technical_details,
        })
    
    def generate_runbook(
        self,
        service_name: str,
        service_description: str,
        dependencies: str,
        common_issues: str
    ) -> str:
        """Generate operational runbook."""
        prompts = self.get_prompts()
        chain = prompts["runbook"] | self.provider.llm | self.output_parser
        
        return chain.invoke({
            "service_name": service_name,
            "service_description": service_description,
            "dependencies": dependencies,
            "common_issues": common_issues,
        })
