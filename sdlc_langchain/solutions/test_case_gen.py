from pydantic import BaseModel, Field
from typing import List
from providers.provider_factory import LLMProviderFactory
from langchain_core.prompts import ChatPromptTemplate

class TestCase(BaseModel):
    id: str
    title: str
    preconditions: str
    steps: List[str]
    expected_result: str
    priority: str = Field(pattern="^(High|Medium|Low)$")

class TestSuite(BaseModel):
    cases: List[TestCase]

def generate_qa_suite(requirement: str):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(TestSuite)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a QA Automation Architect. "
                   "Generate rigorous test cases based on the provided requirements."),
        ("human", "Requirements: {req}")
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({"req": requirement})

if __name__ == "__main__":
    req = "Users must be able to reset their password via email link within 1 hour."
    suite = generate_qa_suite(req)
    for case in suite.cases:
        print(f"Test {case.id}: {case.title} ({case.priority})")
