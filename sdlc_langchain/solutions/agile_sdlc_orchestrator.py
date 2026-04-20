import os
import asyncio
import logging
from typing import TypedDict, List, Annotated, Dict, Any, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from providers.provider_factory import LLMProviderFactory
from config import llm_config
from utils.file_handler import FileHandler

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SDLC-Orchestrator")

# ---- 1. Enhanced Domain Models ---- #

class UserStory(BaseModel):
    id: str = Field(..., description="Unique story ID (e.g., US-001)")
    title: str
    as_a: str
    i_want_to: str
    so_that: str
    acceptance_criteria: List[str] = Field(..., min_items=2)
    priority: Literal["Must", "Should", "Could"] = "Must"
    complexity: int = Field(..., ge=1, le=13)

class PlanningOutput(BaseModel):
    epics: List[str]
    tech_stack: List[str] = Field(..., description="Mandatory technologies to be used")
    architecture_pattern: str = "Microservices"
    user_stories: List[UserStory]

class TestResult(BaseModel):
    passes: bool
    score: float = Field(..., ge=0, le=100)
    feedback: str
    vulnerabilities_found: List[str] = []
    failed_test_cases: List[str] = []

class SDLCState(TypedDict):
    project_name: str
    project_description: str
    tech_stack_preference: List[str]
    requirements: str
    planning: PlanningOutput
    code: str
    tests: str
    test_results: TestResult
    docs: str
    runbook: str
    pipeline_config: str
    dev_attempts: int
    logs: List[str]

# ---- 2. Mega-Prompt Definitions ---- #

MEGA_PROMPTS = {
    "BA": (
        "You are a world-class Senior Business Analyst and Product Manager. "
        "Your task is to transform a vague project intent into a high-fidelity 'Product Requirements Document' (PRD). "
        "Include: Executive Summary, Target Audience, Core Value Proposition, Detailed Functional Requirements, "
        "Non-Functional Requirements (Performance, Security, Scalability), and Potential Risks. "
        "Be verbose, professional, and omit no technical assumptions."
    ),
    "PM": (
        "You are an Elite Agile Project Manager. Break down product requirements into a technical roadmap. "
        "You must define a rigid Tech Stack based on the user's preference and industry best practices. "
        "Create high-granularity User Stories with strict Gherkin-style acceptance criteria. "
        "Identify cross-cutting concerns like logging, observability, and security at the planning level."
    ),
    "DEV": (
        "You are a Principal Software Engineer (L7). Write production-grade, 'Clean Code' principles compliant code. "
        "Adhere strictly to the defined Tech Stack. Use design patterns (Factory, Dependency Injection, etc.) where appropriate. "
        "Focus on modularity, error handling (try/except/logging), and type safety. "
        "You are being evaluated on code maintainability and the 'Principle of Least Surprise'."
    ),
    "QA": (
        "You are a Lead Software Engineer in Test (SDET). Your goal is to break the provided code. "
        "Create a rigorous test suite (Unit, Integration, and Security/Pen-testing). "
        "Simulate execution of these tests against the code. Be hyper-critical. "
        "If you find even a formatting inconsistency or a missing docstring, feedback it. "
        "Analyze for common vulnerabilities (SQLi, XSS, insecure defaults)."
    ),
    "OPS": (
        "You are a Senior Site Reliability Engineer (SRE). Design for 99.99% availability. "
        "Create a fail-safe Operational Runbook and a state-of-the-art DevOps CI/CD pipeline. "
        "Define deployment strategies (Canary/Blue-Green), Monitoring/Alerting thresholds, "
        "and disaster recovery protocols. The pipeline must be defined as valid YAML logic where possible."
    )
}

# ---- 3. Production Node Implementations ---- #

def requirement_node(state: SDLCState):
    provider = LLMProviderFactory.create_from_config()
    logger.info(f"PHASE 1: BA Requirement Gathering for {state['project_name']}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", MEGA_PROMPTS["BA"]),
        ("human", "Project: {name}\nDescription: {desc}\nPreferred Tech: {tech}")
    ])
    
    result = (prompt | provider.llm).invoke({
        "name": state["project_name"], 
        "desc": state["project_description"],
        "tech": state["tech_stack_preference"]
    })
    return {"requirements": result.content, "logs": [f"BA Phase Completed for {state['project_name']}"]}

def planning_node(state: SDLCState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(PlanningOutput)
    logger.info("PHASE 2: PM Agile Planning & Tech-Stack Lockdown")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", MEGA_PROMPTS["PM"]),
        ("human", "PRD Requirements:\n{req}")
    ])
    
    result = structured_llm.invoke({"req": state["requirements"]})
    return {"planning": result}

def development_node(state: SDLCState):
    provider = LLMProviderFactory.create_from_config()
    logger.info(f"PHASE 3: Engineering Development (Attempt {state.get('dev_attempts', 0) + 1})")
    
    feedback_context = ""
    if state.get("test_results") and not state["test_results"].passes:
        feedback_context = (
            f"\n\nCRITICAL FIX REQUIRED (QA SCORE: {state['test_results'].score}/100):\n"
            f"Feedback: {state['test_results'].feedback}\n"
            f"Failed Scenarios: {state['test_results'].failed_test_cases}\n"
            f"Security Risks: {state['test_results'].vulnerabilities_found}"
        )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", MEGA_PROMPTS["DEV"]),
        ("human", "Planning & Tech Stack: {plan}\nRequirements: {req}{feedback}")
    ])
    
    code_result = (prompt | provider.llm).invoke({
        "plan": state["planning"].model_dump_json(), 
        "req": state["requirements"],
        "feedback": feedback_context
    })
    return {"code": code_result.content, "dev_attempts": state.get("dev_attempts", 0) + 1}

def testing_node(state: SDLCState):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(TestResult)
    logger.info("PHASE 4: SDET Audit & Test Execution")
    
    # 1. Generate Test Suite First
    suite_prompt = ChatPromptTemplate.from_messages([
        ("system", MEGA_PROMPTS["QA"]),
        ("human", "Audit this implementation:\n{code}\nAgainst requirements:\n{req}")
    ])
    suite = (suite_prompt | provider.llm).invoke({"code": state["code"], "req": state["requirements"]})
    
    # 2. Extract Structured Result
    result = structured_llm.invoke(
        f"Analyze this test suite: {suite.content}\nAnd this code: {state['code']}\n"
        "Provide final Pass/Fail judgment, Score, and detailed feedback."
    )
    return {"tests": suite.content, "test_results": result}

def documentation_node(state: SDLCState):
    provider = LLMProviderFactory.create_from_config()
    logger.info("PHASE 5: Technical Documentation & Architecture Manual")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Documentation Engineer. Create a high-fidelity documentation site (Markdown)."),
        ("human", "PRD: {req}\nArchitecture & Planning: {plan}\nFinal Code: {code}")
    ])
    
    result = (prompt | provider.llm).invoke({
        "req": state["requirements"],
        "plan": state["planning"].model_dump_json(),
        "code": state["code"]
    })
    return {"docs": result.content}

def operations_node(state: SDLCState):
    provider = LLMProviderFactory.create_from_config()
    logger.info("PHASE 6: SRE Runbook & DevOps Pipeline YAML")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", MEGA_PROMPTS["OPS"]),
        ("human", "Project: {name}\nTech Stack: {tech}\nDocumentation: {docs}")
    ])
    
    result = (prompt | provider.llm).invoke({
        "name": state["project_name"],
        "tech": state["planning"].tech_stack,
        "docs": state["docs"]
    })
    
    # Separate runbook from pipeline if possible (simulated split)
    content = result.content
    runbook = content
    pipeline = "CI/CD YAML Definition Hidden in Content"
    if "```yaml" in content:
        pipeline = content.split("```yaml")[1].split("```")[0]
        
    return {"runbook": runbook, "pipeline_config": pipeline}

# ---- 4. Logic & Routing ---- #

def router(state: SDLCState):
    if state["test_results"].passes or state["dev_attempts"] >= 3:
        return "docs"
    logger.warning(f"Quality Gate Failed (Attempt {state['dev_attempts']}). Retrying...")
    return "dev"

# ---- 5. Graph Assembly ---- #

builder = StateGraph(SDLCState)

builder.add_node("ba", requirement_node)
builder.add_node("pm", planning_node)
builder.add_node("dev", development_node)
builder.add_node("qa", testing_node)
builder.add_node("docs", documentation_node)
builder.add_node("ops", operations_node)

builder.set_entry_point("ba")
builder.add_edge("ba", "pm")
builder.add_edge("pm", "dev")
builder.add_edge("dev", "qa")
builder.add_conditional_edges("qa", router, {"dev": "dev", "docs": "docs"})
builder.add_edge("docs", "ops")
builder.add_edge("ops", END)

# Production checkpointer (In-memory for demo, could be Postgres)
checkpointer = SqliteSaver.from_conn_string(":memory:")
orchestrator = builder.compile(checkpointer=checkpointer)

# ---- 6. High-Performance Runner ---- #

async def run_orchestration():
    print("="*60)
    print("PRODUCTION-GRADE SDLC ORCHESTRATOR [MEGA-PROMPT V2]")
    print("="*60)
    
    # Define your Enterprise Project Goal
    initial_state = {
        "project_name": "SecureBank Ledger",
        "project_description": (
            "A high-availability, double-entry bookkeeping ledger system "
            "with zero-trust architecture, audit logging, and multi-currency support."
        ),
        "tech_stack_preference": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        "dev_attempts": 0,
        "logs": []
    }
    
    config = {"configurable": {"thread_id": "orchestration_001"}}
    
    final_state = await orchestrator.ainvoke(initial_state, config)
    
    print("\n" + "🔥" * 20)
    print("ORCHESTRATION COMPLETE")
    print(f"Final QA Score: {final_state['test_results'].score}/100")
    print(f"Attempts Req: {final_state['dev_attempts']}")
    print("🔥" * 20)
    
    # Persistent Artifact Export
    handler = FileHandler(final_state['project_name'])
    handler.save_stage_output("1_prd_requirements", final_state['requirements'])
    handler.save_stage_output("2_tech_planning", final_state['planning'].model_dump_json())
    handler.save_stage_output("3_final_codebase", final_state['code'])
    handler.save_stage_output("4_test_suite", final_state['tests'])
    handler.save_stage_output("5_technical_docs", final_state['docs'])
    handler.save_stage_output("6_sre_runbook", final_state['runbook'])
    handler.save_stage_output("7_ci_cd_pipeline", final_state['pipeline_config'])
    
    print(f"\n[bold green]Success![/bold green] All artifacts exported to: {handler.base_dir}")

if __name__ == "__main__":
    asyncio.run(run_orchestration())
