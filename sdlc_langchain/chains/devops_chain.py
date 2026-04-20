from typing import Dict, Any

from .base_chain import BaseSDLCChain
from prompts.sdlc_prompts import SDLC_PROMPTS


class DevOpsChain(BaseSDLCChain):
    """Chain for DevOps and CI/CD design."""
    
    @property
    def stage_name(self) -> str:
        return "devops"
    
    def get_prompts(self) -> Dict[str, Any]:
        return SDLC_PROMPTS["devops"]
    
    def design_cicd_pipeline(
        self,
        project_context: str,
        source_control: str = "GitHub",
        deployment_target: str = "Kubernetes",
        environments: str = "dev, staging, production"
    ) -> str:
        """Design CI/CD pipeline."""
        return self.invoke({
            "project_context": project_context,
            "source_control": source_control,
            "deployment_target": deployment_target,
            "environments": environments,
        })
