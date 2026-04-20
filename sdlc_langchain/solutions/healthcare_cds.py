from typing import TypedDict, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from providers.provider_factory import LLMProviderFactory

class ClinicalReview(BaseModel):
    findings: List[str] = Field(description="Key clinical observations")
    contraindications: List[str] = Field(description="Warning signs or medicine clashes")
    recommendation: str
    urgency: str = Field(pattern="^(Routine|Urgent|Emergency)$")
    citations: List[str] = Field(description="Evidence from research or patient history")

class MedicalState(TypedDict):
    patient_query: str
    records: str
    research: str
    final_review: ClinicalReview

def cross_reference_node(state: MedicalState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(ClinicalReview)
    
    print("---PERFORMING CLINICAL REASONING---")
    # In production, this would use RAG over medical journals
    prompt = (
        f"Patient Query: {state['patient_query']}\n"
        f"History: {state['records']}\n"
        f"Research Snippet: {state['research']}\n"
        "Generate a Clinical Decision Support summary with evidence."
    )
    
    review = structured_llm.invoke(prompt)
    return {"final_review": review}

# Graph Construction
workflow = StateGraph(MedicalState)
workflow.add_node("reasoning", cross_reference_node)
workflow.set_entry_point("reasoning")
workflow.add_edge("reasoning", END)

app = workflow.compile()
