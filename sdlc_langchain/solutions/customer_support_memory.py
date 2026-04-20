import os
import sqlite3
from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from providers.provider_factory import LLMProviderFactory
from config import llm_config

# 1. Enhanced State with Metadata
class SupportState(TypedDict):
    messages: Annotated[List[BaseMessage], "Conversation history"]
    user_id: str
    ticket_status: str  # 'open', 'resolved', 'escalated'
    intent: str

# 2. Production Nodes
def assistant_node(state: SupportState):
    provider = LLMProviderFactory.create_from_config()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Support Engineer at SDLC-Tech. "
            "Your goal is to resolve technical issues while maintaining a friendly tone. "
            "Use the conversation history to avoid asking repetitive questions. "
            "If the issue is critical, set ticket_status to 'escalated'."
        )),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | provider.llm
    response = chain.invoke(state)
    
    # Simple logic for intent/status tagging (in production, use structured output)
    status = "open"
    if "escalate" in response.content.lower():
        status = "escalated"
        
    return {"messages": [response], "ticket_status": status}

# 3. Graph with Persistence
workflow = StateGraph(SupportState)
workflow.add_node("agent", assistant_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# Persistence layer
memory = SqliteSaver.from_conn_string(":memory:")
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # Test persistence with thread_id
    config = {"configurable": {"thread_id": "user_123"}}
    
    msg1 = HumanMessage(content="Hi, my checkout is failing with error 402.")
    for chunk in app.stream({"messages": [msg1], "user_id": "123"}, config):
        print(chunk)
