from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class TestingChain(BaseSDLCChain):
    """Chain for test planning."""
    
    @property
    def stage_name(self) -> str:
        return "testing"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["testing"]
    
    def generate_test_plan(
        self,
        project_context: str,
        features_to_test: str,
        requirements_reference: str
    ) -> str:
        """Generate comprehensive test plan."""
        return self.invoke({
            "project_context": project_context,
            "features_to_test": features_to_test,
            "requirements_reference": requirements_reference,
        })
