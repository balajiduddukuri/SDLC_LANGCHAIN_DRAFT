from typing import TypedDict, List
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from providers.provider_factory import LLMProviderFactory

class CodeReview(BaseModel):
    is_correct: bool = Field(description="Whether the code meets requirements")
    feedback: str = Field(description="Specific suggestions for improvement")
    bugs: List[str] = Field(default_factory=list)

class CodeState(TypedDict):
    task: str
    code: str
    review: CodeReview
    attempts: int

def generator_node(state: CodeState):
    provider = LLMProviderFactory.create_from_config()
    print(f"---GENERATION ATTEMPT {state.get('attempts', 0) + 1}---")
    
    prompt = f"Write Python code for: {state['task']}. "
    if state.get("review"):
        prompt += f"Fix these issues: {state['review'].feedback}"
        
    code = provider.llm.invoke(prompt)
    return {"code": code.content, "attempts": state.get("attempts", 0) + 1}

def reviewer_node(state: CodeState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(CodeReview)
    
    print("---REVIEWING CODE---")
    review = structured_llm.invoke(
        f"Task: {state['task']}\nCode: {state['code']}\nPerform strict code review."
    )
    return {"review": review}

def loop_router(state: CodeState):
    if state["review"].is_correct or state["attempts"] >= 3:
        return END
    return "generate"

workflow = StateGraph(CodeState)
workflow.add_node("generate", generator_node)
workflow.add_node("review", reviewer_node)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "review")
workflow.add_conditional_edges("review", loop_router)

app = workflow.compile()
