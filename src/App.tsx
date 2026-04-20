/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import ContextForm from './components/ContextForm';
import OrchestratorDashboard from './components/OrchestratorDashboard';
import { ProjectContext } from './types';
import { Box, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

const INITIAL_CONTEXT: ProjectContext = {
  projectName: "AI Cloud Platform",
  projectDescription: "A scalable platform for deploying and monitoring AI agents with built-in observability.",
  businessDomain: "SaaS / AI Infrastructure",
  techStack: ["Node.js", "React", "PostgreSQL", "Redis", "Docker"],
  programmingLanguages: ["TypeScript", "Rust"],
  frameworks: ["Express", "Next.js", "Tailwind CSS"],
  cloudProvider: "GCP",
  databaseTypes: ["PostgreSQL", "Redis"],
  expectedUsers: 10000,
  expectedRequestsPerSecond: 100,
  dataVolumeGb: 50,
  features: [
    "Multi-tenant Authentication",
    "Real-time Monitoring",
    "Automated Deployment",
    "Billing & Usage Tracking"
  ],
  userRoles: ["Admin", "Developer", "Analyst"],
  integrations: ["Stripe", "Prometheus", "GitHub"],
  complianceRequirements: ["GDPR", "SOC2"],
  securityLevel: "High",
  teamSize: 5,
  developmentMethodology: "Agile",
  businessRequirements: "The system must support automatic failover and ensure 99.9% availability for critical agent services."
};

export default function App() {
  const [context, setContext] = React.useState<ProjectContext>(INITIAL_CONTEXT);
  const [view, setView] = React.useState<'form' | 'dashboard'>('form');

  return (
    <div className="min-h-screen bg-[#050505] text-neutral-300 font-sans selection:bg-blue-500/30 selection:text-white">
      {/* Header */}
      <header className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center shadow-[0_0_15px_rgba(37,99,235,0.5)]">
              <Layers size={18} className="text-white" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tighter text-white uppercase italic">SDLC</span>
              <span className="text-neutral-500 font-mono text-[10px] block -mt-1 tracking-widest">ORCHESTRATOR</span>
            </div>
          </div>
          
          <nav className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-4 text-[10px] uppercase font-bold tracking-[0.2em] text-neutral-500">
               <span className="text-blue-500/50">Runtime: Gemini-3-Flash</span>
               <span className="w-1 h-1 bg-neutral-800 rounded-full"></span>
               <span>Mode: Production</span>
            </div>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {view === 'form' ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="mb-12">
                <h1 className="text-5xl font-bold text-white tracking-tighter mb-4">
                  Define Project <span className="text-neutral-500 italic">Parameters</span>
                </h1>
                <p className="max-w-2xl text-neutral-400 leading-relaxed font-mono text-sm">
                  Initialize your system design by providing the technical and business context. 
                  Our transformer models will generate a complete SDLC documentation suite.
                </p>
              </div>
              <ContextForm 
                context={context} 
                setContext={setContext} 
                onStart={() => setView('dashboard')} 
              />
            </motion.div>
          ) : (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              <OrchestratorDashboard 
                context={context} 
                onReset={() => setView('form')} 
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Decorative Elements */}
      <div className="fixed bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neutral-800 to-transparent pointer-events-none"></div>
      <div className="fixed top-0 left-0 w-[1px] h-full bg-gradient-to-b from-transparent via-neutral-800 to-transparent pointer-events-none"></div>
    </div>
  );
}

