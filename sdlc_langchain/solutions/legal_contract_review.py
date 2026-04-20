from pydantic import BaseModel, Field
from typing import List
from providers.provider_factory import LLMProviderFactory

class ComplianceIssue(BaseModel):
    clause: str
    risk_level: str = Field(pattern="^(None|Low|Medium|High|Critical)$")
    missing: bool
    remediation_text: str

class ContractAudit(BaseModel):
    is_compliant: bool
    issues: List[ComplianceIssue]
    overall_summary: str

def audit_contract(contract_text: str):
    provider = LLMProviderFactory.create_from_config()
    structured_llm = provider.llm.with_structured_output(ContractAudit)
    
    system_rules = """
    Validate the contract against these mandates:
    1. Must have explicitly stated 30-day termination for convenience.
    2. Must have mutual indemnification.
    3. Auto-renewal must NOT exceed 1 year.
    4. Governing law must be New York or Delaware.
    """
    
    print("---LEGAL RULE ENFORCEMENT ENGINE RUNNING---")
    audit = structured_llm.invoke(f"{system_rules}\n\nContract Text: {contract_text}")
    return audit

if __name__ == "__main__":
    sample = "This contract renews for 5 years automatically. Termination requires cause."
    audit = audit_contract(sample)
    print(f"Compliance Status: {audit.is_compliant}")
    for i in audit.issues:
        print(f"[{i.risk_level}] {i.clause}: {i.remediation_text}")
