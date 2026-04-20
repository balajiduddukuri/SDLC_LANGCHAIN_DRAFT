import { SDLCStage } from "./types";

export const STAGE_CONFIG: Record<SDLCStage, { title: string; dependencies: SDLCStage[] }> = {
  requirements: { title: "Requirements Analysis", dependencies: [] },
  architecture: { title: "System Architecture", dependencies: ["requirements"] },
  database: { title: "Database Design", dependencies: ["architecture"] },
  api: { title: "API Design", dependencies: ["architecture"] },
  security: { title: "Security Architecture", dependencies: ["architecture"] },
  implementation: { title: "Implementation Plan", dependencies: ["architecture", "database", "api"] },
  testing: { title: "Testing Strategy", dependencies: ["requirements", "implementation"] },
  devops: { title: "DevOps & CI/CD", dependencies: ["architecture", "implementation"] },
  monitoring: { title: "Monitoring & Observability", dependencies: ["architecture", "devops"] },
  documentation: { title: "Documentation", dependencies: ["implementation", "testing"] },
};

export const PROMPTS: Record<SDLCStage, string> = {
  requirements: `Analyze the following project context and extract requirements.
{project_context}

BUSINESS REQUIREMENTS:
{business_requirements}

Create a comprehensive requirements specification including:
1. FUNCTIONAL REQUIREMENTS (Priority Must/Should/Could)
2. NON-FUNCTIONAL REQUIREMENTS (Performance, Scalability, Security, Availability)
3. USER ROLES AND PERMISSIONS
4. INTEGRATION REQUIREMENTS
5. DATA REQUIREMENTS
6. CONSTRAINTS AND ASSUMPTIONS`,

  architecture: `Design a comprehensive system architecture.
{project_context}

REQUIREMENTS SUMMARY:
{requirements_summary}

Create a detailed architecture document including:
1. ARCHITECTURE OVERVIEW & JUSTIFICATION
2. COMPONENT ARCHITECTURE
3. DATA ARCHITECTURE
4. INTEGRATION ARCHITECTURE
5. INFRASTRUCTURE ARCHITECTURE
6. CROSS-CUTTING CONCERNS
7. TECHNOLOGY STACK TABLE
8. ARCHITECTURE DECISION RECORDS`,

  database: `Design the database schema.
{project_context}
ARCHITECTURE SUMMARY:
{architecture_summary}
DATA REQUIREMENTS:
{data_requirements}

Create a database design including:
1. DATABASE STRATEGY & JUSTIFICATION
2. ENTITY RELATIONSHIP MODEL
3. INDEXING STRATEGY
4. PARTITIONING STRATEGY
5. REPLICATION & HIGH AVAILABILITY
6. BACKUP & RECOVERY
7. DDL SCRIPTS (Propose table creation)`,

  api: `Design RESTful APIs for {service_name}.
{project_context}
ARCHITECTURE SUMMARY:
{architecture_summary}

Create an API design including:
1. API OVERVIEW (Style, Base URL, Versioning)
2. AUTHENTICATION & AUTHORIZATION
3. API ENDPOINTS (Methods, Schemas, Status codes)
4. ERROR HANDLING
5. RATE LIMITING & PAGINATION
6. OPENAPI SPECIFICATION (YAML format)`,

  security: `Design security architecture.
{project_context}
ARCHITECTURE SUMMARY:
{architecture_summary}
COMPLIANCE: {compliance_requirements}

Create a security design including: 
1. IDENTITY & ACCESS MANAGEMENT
2. DATA SECURITY (Encryption, Key MGMT)
3. NETWORK SECURITY
4. APPLICATION SECURITY
5. SECRET MANAGEMENT
6. LOGGING & MONITORING
7. INCIDENT RESPONSE`,

  implementation: `Create a detailed implementation plan.
{project_context}
ARCHITECTURE: {architecture_summary}
DATABASE: {database_summary}
API: {api_summary}

Include:
1. Project structure and code organization
2. Development phases and milestones
3. Technical specifications for key components
4. Coding standards and best practices
5. Development environment setup
6. Third-party library recommendations`,

  testing: `Create a comprehensive test plan.
{project_context}
FEATURES: {features_to_test}
REQUIREMENTS: {requirements_reference}

Include:
1. TEST STRATEGY (Unit, Integration, E2E)
2. TEST ENVIRONMENT & DATA MANAGEMENT
3. DEFECT MANAGEMENT
4. QUALITY GATES & METRICS
5. SCHEDULE & RESOURCES`,

  devops: `Design CI/CD pipeline.
{project_context}
SOURCE CONTROL: {source_control}
DEPLOYMENT TARGET: {deployment_target}
ENVIRONMENTS: {environments}

Include:
1. PIPELINE OVERVIEW & BRANCHING STRATEGY
2. CI STAGES (Build, Test, Security)
3. CD STAGES (Promotion flow)
4. DEPLOYMENT STRATEGIES (Blue-green, Canary)
5. ARTIFACT MANAGEMENT
6. PIPELINE AS CODE EXAMPLE`,

  monitoring: `Design observability strategy.
{project_context}
ARCHITECTURE: {architecture_summary}
SLA: {sla_requirements}

Include:
1. METRICS (USE/RED)
2. LOGGING STRATEGY
3. DISTRIBUTED TRACING
4. ALERTING & DASHBOARDS
5. SLIs AND SLOs
6. ON-CALL ESCALATION`,

  documentation: `Generate technical documentation and runbook.
{project_context}
ARCHITECTURE: {architecture_summary}
IMPLEMENTATION: {implementation_summary}

Include:
1. OVERVIEW
2. GETTING STARTED
3. API REFERENCE
4. DEVELOPMENT GUIDE
5. OPERATIONAL RUNBOOK (Health checks, Procedures, Common issues)`
};
