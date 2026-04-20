export type StageStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface ProjectContext {
  projectName: string;
  projectDescription: string;
  businessDomain: string;
  techStack: string[];
  programmingLanguages: string[];
  frameworks: string[];
  cloudProvider: string;
  databaseTypes: string[];
  expectedUsers: number;
  expectedRequestsPerSecond: number;
  dataVolumeGb: number;
  features: string[];
  userRoles: string[];
  integrations: string[];
  complianceRequirements: string[];
  securityLevel: string;
  teamSize: number;
  developmentMethodology: string;
  businessRequirements: string;
}

export interface StageResult {
  id: string;
  title: string;
  content: string;
  status: StageStatus;
  tokensUsed?: number;
  executionTime?: number;
}

export type SDLCStage = 
  | 'requirements'
  | 'architecture'
  | 'database'
  | 'api'
  | 'security'
  | 'implementation'
  | 'testing'
  | 'devops'
  | 'monitoring'
  | 'documentation';
