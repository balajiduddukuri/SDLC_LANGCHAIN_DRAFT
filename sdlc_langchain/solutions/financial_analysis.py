from pydantic import BaseModel, Field
from typing import List
from providers.provider_factory import LLMProviderFactory
from langchain_core.prompts import ChatPromptTemplate

class FinancialInsights(BaseModel):
    revenue: float = Field(description="Total revenue in USD")
    ebitda: float = Field(description="EBITDA amount")
    growth_yoy: str = Field(description="Year-on-year growth percentage")
    risk_factors: List[str] = Field(description="Top 3 risk factors mentioned")
    sentiment: str = Field(description="Overall financial sentiment (Bullish/Bearish/Neutral)")

def extract_financials(report_text: str):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(FinancialInsights)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional Financial Analyst at a top-tier hedge fund."),
        ("human", "Analyze the following quarterly earnings text and extract key KPIs: {text}")
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({"text": report_text})

if __name__ == "__main__":
    mock_report = "Revenue was $10.5B, an 8% increase from last year. EBITDA hit $2.1B. Risks include supply chain and inflation."
    print(extract_financials(mock_report))
