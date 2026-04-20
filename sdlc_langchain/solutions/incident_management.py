from typing import TypedDict, List, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from providers.provider_factory import LLMProviderFactory

class Diagnostic(BaseModel):
    root_cause: str = Field(description="Identified cause of failure")
    severity: Literal["low", "medium", "high", "critical"]
    recommended_action: str

class IncidentState(TypedDict):
    alert_payload: dict
    logs: List[str]
    diagnostic: Diagnostic
    fix_applied: bool

def log_fetcher_node(state: IncidentState):
    print("---FETCHING RELEVANT LOGS---")
    # Simulate tool call to CloudWatch/Elasticsearch
    return {"logs": ["500 Internal Server Error", "OutOfMemoryError: Java heap space"]}

def diagnosis_node(state: IncidentState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(Diagnostic)
    
    print("---AI DIAGNOSIS IN PROGRESS---")
    result = structured_llm.invoke(f"Analyze these logs: {state['logs']}")
    return {"diagnostic": result}

def automation_gate(state: IncidentState):
    """Router: Apply automatic fix or escalate to human?"""
    if state["diagnostic"].severity == "critical":
        print("---ESCALATING TO ON-CALL ENGINEER---")
        return END
    return "apply_fix"

def application_node(state: IncidentState):
    print(f"---APPLYING FIX: {state['diagnostic'].recommended_action}---")
    return {"fix_applied": True}

workflow = StateGraph(IncidentState)
workflow.add_node("fetch_logs", log_fetcher_node)
workflow.add_node("diagnose", diagnosis_node)
workflow.add_node("apply_fix", application_node)

workflow.set_entry_point("fetch_logs")
workflow.add_edge("fetch_logs", "diagnose")
workflow.add_conditional_edges("diagnose", automation_gate, {"apply_fix": "apply_fix", END: END})
workflow.add_edge("apply_fix", END)

app = workflow.compile()
