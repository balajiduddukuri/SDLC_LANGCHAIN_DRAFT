from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from providers.provider_factory import LLMProviderFactory

# 1. Structured Schemas
class ExtractedData(BaseModel):
    entities: List[str] = Field(description="Names of organizations and persons")
    dates: List[str] = Field(description="Important dates found in document")
    values: List[str] = Field(description="Financial amounts or terms")

class DocState(TypedDict):
    content: str
    metadata: ExtractedData
    summary: str
    is_valid: bool

# 2. Optimized Nodes
def extraction_node(state: DocState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(ExtractedData)
    
    print("---EXTRACTING STRUCTURED DATA---")
    result = structured_llm.invoke(f"Extract key data from: {state['content']}")
    return {"metadata": result}

def validation_node(state: DocState):
    print("---VALIDATING---")
    # Real logic: ensure values were actually found
    is_valid = len(state["metadata"].values) > 0
    return {"is_valid": is_valid}

def router(state: DocState):
    if state["is_valid"]:
        return "summarize"
    return END

def summary_node(state: DocState):
    provider = LLMProviderFactory.create_from_config()
    print("---GENERATING EXECUTIVE SUMMARY---")
    summary = provider.llm.invoke(f"Summarize this based on metadata: {state['metadata']}")
    return {"summary": summary.content}

# 3. Build Graph
workflow = StateGraph(DocState)
workflow.add_node("extract", extraction_node)
workflow.add_node("validate", validation_node)
workflow.add_node("summarize", summary_node)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "validate")
workflow.add_conditional_edges("validate", router, {"summarize": "summarize", END: END})
workflow.add_edge("summarize", END)

app = workflow.compile()
