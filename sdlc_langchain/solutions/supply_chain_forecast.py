from typing import TypedDict, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from providers.provider_factory import LLMProviderFactory

class Strategy(BaseModel):
    demand_forecast: str
    inventory_action: str = Field(description="Buy / Sell / Hold / Move")
    confidence: float
    reasoning: str

class ForecastState(TypedDict):
    data_points: List[float]
    signals: List[str]
    output: Strategy

def reasoning_layer(state: ForecastState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(Strategy)
    
    print("---ORCHESTRATING HYBRID AI WORKFLOW---")
    prompt = (
        f"Historical Data (Last 5 periods): {state['data_points']}\n"
        f"External Signals: {state['signals']}\n"
        "Analyze the trend and suggest an inventory strategy."
    )
    
    result = structured_llm.invoke(prompt)
    return {"output": result}

workflow = StateGraph(ForecastState)
workflow.add_node("brain", reasoning_layer)
workflow.set_entry_point("brain")
workflow.add_edge("brain", END)

app = workflow.compile()
