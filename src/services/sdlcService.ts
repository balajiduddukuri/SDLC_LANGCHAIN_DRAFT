import { GoogleGenAI } from "@google/genai";
import { PROMPTS } from "../constants";
import { ProjectContext, SDLCStage } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export async function generateStageContent(
  stage: SDLCStage,
  context: ProjectContext,
  previousResults: Record<string, string>,
  onChunk?: (chunk: string) => void
): Promise<string> {
  const promptTemplate = PROMPTS[stage];
  
  // Format context string as in the python script
  const contextString = `
PROJECT CONTEXT:
================
Project Name: ${context.projectName}
Description: ${context.projectDescription}
Business Domain: ${context.businessDomain}

TECHNICAL STACK:
- Languages: ${context.programmingLanguages.join(", ")}
- Frameworks: ${context.frameworks.join(", ")}
- Cloud Provider: ${context.cloudProvider}
- Databases: ${context.databaseTypes.join(", ")}

SCALE REQUIREMENTS:
- Expected Users: ${context.expectedUsers.toLocaleString()}
- Requests/Second: ${context.expectedRequestsPerSecond}
- Data Volume: ${context.dataVolumeGb} GB

FEATURES:
${context.features.map(f => `- ${f}`).join("\n")}

USER ROLES:
${context.userRoles.map(r => `- ${r}`).join("\n")}

INTEGRATIONS:
${context.integrations.map(i => `- ${i}`).join("\n")}

COMPLIANCE: ${context.complianceRequirements.join(", ") || 'None specified'}
SECURITY LEVEL: ${context.securityLevel}

TEAM SIZE: ${context.teamSize}
METHODOLOGY: ${context.developmentMethodology}
`;

  let prompt = promptTemplate.replace("{project_context}", contextString);

  // Handle stage dependent variables
  switch (stage) {
    case 'requirements':
      prompt = prompt.replace("{business_requirements}", context.businessRequirements);
      break;
    case 'architecture':
      prompt = prompt.replace("{requirements_summary}", previousResults.requirements || "");
      break;
    case 'database':
      prompt = prompt.replace("{architecture_summary}", previousResults.architecture || "");
      prompt = prompt.replace("{data_requirements}", `Features: ${context.features.join(", ")}`);
      break;
    case 'api':
      prompt = prompt.replace("{architecture_summary}", previousResults.architecture || "");
      prompt = prompt.replace("{service_name}", context.projectName);
      break;
    case 'security':
      prompt = prompt.replace("{architecture_summary}", previousResults.architecture || "");
      prompt = prompt.replace("{compliance_requirements}", context.complianceRequirements.join(", "));
      break;
    case 'implementation':
      prompt = prompt.replace("{architecture_summary}", previousResults.architecture || "");
      prompt = prompt.replace("{database_summary}", previousResults.database || "");
      prompt = prompt.replace("{api_summary}", previousResults.api || "");
      break;
    case 'testing':
      prompt = prompt.replace("{features_to_test}", context.features.join(", "));
      prompt = prompt.replace("{requirements_reference}", previousResults.requirements || "");
      break;
    case 'devops':
      prompt = prompt.replace("{source_control}", "GitHub");
      prompt = prompt.replace("{deployment_target}", "Kubernetes");
      prompt = prompt.replace("{environments}", "dev, staging, production");
      break;
    case 'monitoring':
      prompt = prompt.replace("{architecture_summary}", previousResults.architecture || "");
      prompt = prompt.replace("{sla_requirements}", "99.9% availability");
      break;
    case 'documentation':
      prompt = prompt.replace("{architecture_summary}", previousResults.architecture || "");
      prompt = prompt.replace("{implementation_summary}", previousResults.implementation || "");
      break;
  }

  try {
    const stream = await ai.models.generateContentStream({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        temperature: 0.3,
        topP: 0.95,
      }
    });

    let fullText = "";
    for await (const chunk of stream) {
      const chunkText = chunk.text;
      fullText += chunkText;
      if (onChunk) onChunk(chunkText);
    }
    return fullText;
  } catch (error) {
    console.error(`Error generating content for ${stage}:`, error);
    throw error;
  }
}
