from langchain.prompts import PromptTemplate

# Requirements Prompts
REQUIREMENTS_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["project_context", "business_requirements"],
    template="""
You are a Senior Business Analyst. Analyze the following project context and extract requirements.

{project_context}

BUSINESS REQUIREMENTS:
{business_requirements}

Create a comprehensive requirements specification including:

## 1. FUNCTIONAL REQUIREMENTS
List all functional requirements categorized by feature area with priority (Must Have/Should Have/Could Have).

## 2. NON-FUNCTIONAL REQUIREMENTS
- Performance requirements
- Scalability requirements
- Security requirements
- Availability requirements

## 3. USER ROLES AND PERMISSIONS
Define each user role and their permissions.

## 4. INTEGRATION REQUIREMENTS
List all external system integrations.

## 5. DATA REQUIREMENTS
- Data entities
- Data retention policies
- Privacy considerations

## 6. CONSTRAINTS AND ASSUMPTIONS
List all identified constraints and assumptions.
"""
)

USER_STORY_PROMPT = PromptTemplate(
    input_variables=["project_context", "feature_name", "feature_description"],
    template="""
Generate user stories for the following feature:

{project_context}

FEATURE: {feature_name}
DESCRIPTION: {feature_description}

For each user story, provide:
- As a [user role], I want to [action], so that [benefit]
- Acceptance criteria (Given/When/Then format)
- Story points estimate (1/2/3/5/8/13)
- Priority (Critical/High/Medium/Low)
"""
)

# Architecture Prompts
ARCHITECTURE_DESIGN_PROMPT = PromptTemplate(
    input_variables=["project_context", "requirements_summary"],
    template="""
You are a Solutions Architect. Design a comprehensive system architecture.

{project_context}

REQUIREMENTS SUMMARY:
{requirements_summary}

Create a detailed architecture document including:

## 1. ARCHITECTURE OVERVIEW
- Architecture style and justification
- High-level component diagram description

## 2. COMPONENT ARCHITECTURE
For each component: name, responsibility, technology, interfaces

## 3. DATA ARCHITECTURE
- Data flow between components
- Data storage strategy

## 4. INTEGRATION ARCHITECTURE
- API Gateway, Service mesh, Message queues

## 5. INFRASTRUCTURE ARCHITECTURE
- Cloud services, Network topology, Load balancing

## 6. CROSS-CUTTING CONCERNS
- Authentication, Logging, Error handling

## 7. TECHNOLOGY STACK
| Layer | Technology | Justification |

## 8. ARCHITECTURE DECISION RECORDS
Key decisions with context, options, and consequences
"""
)

# Database Prompts
DATABASE_DESIGN_PROMPT = PromptTemplate(
    input_variables=["project_context", "architecture_summary", "data_requirements"],
    template="""
You are a Database Architect. Design the database schema.

{project_context}

ARCHITECTURE SUMMARY:
{architecture_summary}

DATA REQUIREMENTS:
{data_requirements}

Create a database design including:

## 1. DATABASE STRATEGY
- Database types and justification
- Polyglot persistence approach

## 2. ENTITY RELATIONSHIP MODEL
For each entity: columns, types, constraints, indexes

## 3. INDEXING STRATEGY
- Primary, secondary, and composite indexes

## 4. PARTITIONING STRATEGY
- Partition type and key selection

## 5. REPLICATION & HIGH AVAILABILITY
- Replication topology, failover strategy

## 6. BACKUP & RECOVERY
- Backup frequency, retention, RPO/RTO

## 7. DDL SCRIPTS
Provide table creation scripts
"""
)

# API Design Prompts
API_DESIGN_PROMPT = PromptTemplate(
    input_variables=["project_context", "architecture_summary", "service_name"],
    template="""
You are an API Architect. Design RESTful APIs.

{project_context}

ARCHITECTURE SUMMARY:
{architecture_summary}

SERVICE: {service_name}

Create an API design including:

## 1. API OVERVIEW
- API style, base URL, versioning strategy

## 2. AUTHENTICATION & AUTHORIZATION
- Auth method, token format, RBAC model

## 3. API ENDPOINTS
For each resource:
- HTTP methods and endpoints
- Request/Response schemas
- Status codes

## 4. ERROR HANDLING
Standard error response format

## 5. RATE LIMITING
Rate limit tiers and headers

## 6. PAGINATION
Pagination approach

## 7. OPENAPI SPECIFICATION
Provide OpenAPI 3.0 YAML
"""
)

# Security Prompts
SECURITY_DESIGN_PROMPT = PromptTemplate(
    input_variables=["project_context", "architecture_summary", "compliance_requirements"],
    template="""
You are a Security Architect. Design security architecture.

{project_context}

ARCHITECTURE SUMMARY:
{architecture_summary}

COMPLIANCE: {compliance_requirements}

Create a security design including:

## 1. IDENTITY & ACCESS MANAGEMENT
- Authentication methods, MFA, session management
- Authorization model (RBAC/ABAC)

## 2. DATA SECURITY
- Encryption at rest and in transit
- Key management, data classification

## 3. NETWORK SECURITY
- VPC design, security groups, WAF

## 4. APPLICATION SECURITY
- Input validation, security headers

## 5. SECRET MANAGEMENT
- Secrets storage, rotation policies

## 6. LOGGING & MONITORING
- Security event logging, SIEM integration

## 7. INCIDENT RESPONSE
- Response procedures, communication plan
"""
)

# Testing Prompts
TEST_PLAN_PROMPT = PromptTemplate(
    input_variables=["project_context", "features_to_test", "requirements_reference"],
    template="""
You are a QA Architect. Create a test plan.

{project_context}

FEATURES: {features_to_test}

REQUIREMENTS: {requirements_reference}

Create a test plan including:

## 1. TEST STRATEGY
- Unit testing approach and coverage targets
- Integration testing scenarios
- E2E test cases
- Performance testing requirements

## 2. TEST ENVIRONMENT
- Environment topology
- Test data management

## 3. TEST DATA
- Data requirements and generation

## 4. DEFECT MANAGEMENT
- Severity and priority definitions

## 5. METRICS
- Metrics to track, quality gates

## 6. SCHEDULE
- Phase timeline, resource allocation
"""
)

# DevOps Prompts
CICD_PIPELINE_PROMPT = PromptTemplate(
    input_variables=["project_context", "source_control", "deployment_target", "environments"],
    template="""
You are a DevOps Engineer. Design CI/CD pipeline.

{project_context}

SOURCE CONTROL: {source_control}
DEPLOYMENT TARGET: {deployment_target}
ENVIRONMENTS: {environments}

Create a CI/CD design including:

## 1. PIPELINE OVERVIEW
- Branching strategy
- Environment promotion flow

## 2. CI STAGES
- Build, Test, Security scan, Quality gates

## 3. CD STAGES
- Deployment to each environment
- Approval gates

## 4. DEPLOYMENT STRATEGIES
- Blue-green, canary, rolling updates

## 5. ARTIFACT MANAGEMENT
- Container registry, versioning

## 6. ROLLBACK PROCEDURES
- Automatic and manual rollback

## 7. PIPELINE AS CODE
Provide pipeline configuration
"""
)

# Monitoring Prompts
OBSERVABILITY_PROMPT = PromptTemplate(
    input_variables=["project_context", "architecture_summary", "sla_requirements"],
    template="""
You are an SRE Architect. Design observability strategy.

{project_context}

ARCHITECTURE: {architecture_summary}
SLA: {sla_requirements}

Create an observability design including:

## 1. METRICS (USE/RED)
- System metrics, service metrics, business metrics

## 2. LOGGING STRATEGY
- Log levels, format, aggregation

## 3. DISTRIBUTED TRACING
- Tool selection, sampling strategy

## 4. ALERTING
- Severity levels, alert rules

## 5. DASHBOARDS
- Executive, operations, service dashboards

## 6. SLIs AND SLOs
- Availability, latency, throughput SLOs

## 7. ON-CALL
- Rotation, escalation matrix
"""
)

# Documentation Prompts
TECHNICAL_DOC_PROMPT = PromptTemplate(
    input_variables=["component_name", "component_purpose", "technical_details"],
    template="""
Create technical documentation for:

COMPONENT: {component_name}
PURPOSE: {component_purpose}
DETAILS: {technical_details}

Include:

## 1. OVERVIEW
- Component description, role in system

## 2. GETTING STARTED
- Prerequisites, installation, configuration

## 3. API REFERENCE
- All public APIs/interfaces

## 4. DEVELOPMENT GUIDE
- Code structure, coding standards

## 5. DEPLOYMENT
- Environment details, deployment process

## 6. TROUBLESHOOTING
- Common issues and solutions

## 7. FAQ
"""
)

RUNBOOK_PROMPT = PromptTemplate(
    input_variables=["service_name", "service_description", "dependencies", "common_issues"],
    template="""
Create an operational runbook for:

SERVICE: {service_name}
DESCRIPTION: {service_description}
DEPENDENCIES: {dependencies}
COMMON ISSUES: {common_issues}

Include:

## 1. SERVICE OVERVIEW
- Description, criticality, SLA reference

## 2. HEALTH CHECKS
- Endpoints, expected responses

## 3. OPERATIONAL PROCEDURES
- Start, stop, restart, scale

## 4. COMMON ALERTS
- Alert descriptions, triage steps, resolution

## 5. TROUBLESHOOTING
- Decision tree for common issues

## 6. BACKUP AND RECOVERY
- Backup schedule, recovery procedures

## 7. CONTACTS
- On-call, escalation paths
"""
)

# Prompt Registry
SDLC_PROMPTS = {
    "requirements": {
        "extraction": REQUIREMENTS_EXTRACTION_PROMPT,
        "user_stories": USER_STORY_PROMPT,
    },
    "architecture": {
        "design": ARCHITECTURE_DESIGN_PROMPT,
    },
    "database": {
        "design": DATABASE_DESIGN_PROMPT,
    },
    "api": {
        "design": API_DESIGN_PROMPT,
    },
    "security": {
        "design": SECURITY_DESIGN_PROMPT,
    },
    "testing": {
        "plan": TEST_PLAN_PROMPT,
    },
    "devops": {
        "cicd": CICD_PIPELINE_PROMPT,
    },
    "monitoring": {
        "observability": OBSERVABILITY_PROMPT,
    },
    "documentation": {
        "technical": TECHNICAL_DOC_PROMPT,
        "runbook": RUNBOOK_PROMPT,
    },
}
