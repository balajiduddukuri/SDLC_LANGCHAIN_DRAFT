from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class CloudProvider(str, Enum):
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    ON_PREMISE = "On-Premise"
    HYBRID = "Hybrid"


class DatabaseType(str, Enum):
    POSTGRESQL = "PostgreSQL"
    MYSQL = "MySQL"
    MONGODB = "MongoDB"
    DYNAMODB = "DynamoDB"
    REDIS = "Redis"
    ELASTICSEARCH = "Elasticsearch"


class ProjectContext(BaseModel):
    """Complete project context for SDLC documentation generation."""
    
    # Basic Info
    project_name: str = Field(..., description="Name of the project")
    project_description: str = Field(..., description="Brief description of the project")
    business_domain: str = Field(..., description="Business domain (e.g., E-commerce, Healthcare)")
    
    # Technical Context
    tech_stack: List[str] = Field(default_factory=list, description="Technologies to be used")
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    cloud_provider: CloudProvider = Field(default=CloudProvider.AWS)
    database_types: List[DatabaseType] = Field(default_factory=list)
    
    # Scale & Performance
    expected_users: int = Field(default=1000, description="Expected number of users")
    expected_requests_per_second: int = Field(default=100)
    data_volume_gb: int = Field(default=100)
    
    # Requirements
    features: List[str] = Field(default_factory=list, description="List of features")
    user_roles: List[str] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list, description="External systems to integrate")
    
    # Compliance & Security
    compliance_requirements: List[str] = Field(default_factory=list)
    security_level: str = Field(default="Standard")
    
    # Team & Process
    team_size: int = Field(default=5)
    development_methodology: str = Field(default="Agile")
    
    # Additional Context
    existing_systems: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    business_requirements: str = Field(default="")
    
    def to_context_string(self) -> str:
        """Convert context to a formatted string for prompts."""
        return f"""
PROJECT CONTEXT:
================
Project Name: {self.project_name}
Description: {self.project_description}
Business Domain: {self.business_domain}

TECHNICAL STACK:
- Languages: {', '.join(self.programming_languages)}
- Frameworks: {', '.join(self.frameworks)}
- Cloud Provider: {self.cloud_provider.value}
- Databases: {', '.join([db.value for db in self.database_types])}

SCALE REQUIREMENTS:
- Expected Users: {self.expected_users:,}
- Requests/Second: {self.expected_requests_per_second}
- Data Volume: {self.data_volume_gb} GB

FEATURES:
{chr(10).join(f'- {feature}' for feature in self.features)}

USER ROLES:
{chr(10).join(f'- {role}' for role in self.user_roles)}

INTEGRATIONS:
{chr(10).join(f'- {integration}' for integration in self.integrations)}

COMPLIANCE: {', '.join(self.compliance_requirements) if self.compliance_requirements else 'None specified'}
SECURITY LEVEL: {self.security_level}

TEAM SIZE: {self.team_size}
METHODOLOGY: {self.development_methodology}

CONSTRAINTS:
{chr(10).join(f'- {constraint}' for constraint in self.constraints)}
"""


class SDLCOutput(BaseModel):
    """Container for all SDLC stage outputs."""
    requirements: Optional[str] = None
    user_stories: Optional[str] = None
    architecture: Optional[str] = None
    database_design: Optional[str] = None
    api_design: Optional[str] = None
    security_design: Optional[str] = None
    implementation_plan: Optional[str] = None
    test_plan: Optional[str] = None
    devops_pipeline: Optional[str] = None
    monitoring_strategy: Optional[str] = None
    documentation: Optional[str] = None
    runbook: Optional[str] = None
