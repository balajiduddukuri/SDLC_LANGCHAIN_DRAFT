from typing import Dict, Any

from .base_chain import BaseSDLCChain


class ImplementationChain(BaseSDLCChain):
    """Chain for implementation planning."""
    
    @property
    def stage_name(self) -> str:
        return "implementation"
    
    def get_prompts(self) -> Dict[str, Any]:
        from langchain.prompts import PromptTemplate
        return {
            "main": PromptTemplate(
                input_variables=["project_context"],
                template="""
Create an implementation plan for:

{project_context}

Include:
1. Project structure and code organization
2. Development phases and milestones
3. Technical specifications for key components
4. Coding standards and best practices
5. Development environment setup
6. Third-party library recommendations
"""
            )
        }
