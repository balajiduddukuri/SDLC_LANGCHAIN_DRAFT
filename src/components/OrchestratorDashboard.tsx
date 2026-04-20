import React from 'react';
import { SDLCStage, StageResult, ProjectContext } from '../types';
import { STAGE_CONFIG } from '../constants';
import { generateStageContent } from '../services/sdlcService';
import { CheckCircle2, Circle, Loader2, AlertCircle, FileText, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../lib/utils';

interface Props {
  context: ProjectContext;
  onReset: () => void;
}

export default function OrchestratorDashboard({ context, onReset }: Props) {
  const [results, setResults] = React.useState<Record<string, StageResult>>({});
  const [currentStage, setCurrentStage] = React.useState<SDLCStage | null>(null);
  const [streamingText, setStreamingText] = React.useState("");
  const [selectedResult, setSelectedResult] = React.useState<string | null>(null);

  const stages = Object.keys(STAGE_CONFIG) as SDLCStage[];

  const runPipeline = async () => {
    const stageOrder = stages;
    
    for (const stage of stageOrder) {
      setCurrentStage(stage);
      setStreamingText("");
      
      setResults(prev => ({
        ...prev,
        [stage]: { id: stage, title: STAGE_CONFIG[stage].title, content: "", status: 'running' }
      }));

      try {
        const previousOutputs: Record<string, string> = {};
        Object.entries(results).forEach(([k, v]) => {
          previousOutputs[k] = (v as StageResult).content;
        });

        const content = await generateStageContent(stage, context, previousOutputs, (chunk) => {
          setStreamingText(prev => prev + chunk);
        });

        setResults(prev => ({
          ...prev,
          [stage]: { ...prev[stage], content, status: 'completed' }
        }));
      } catch (error) {
        setResults(prev => ({
          ...prev,
          [stage]: { ...prev[stage], status: 'failed' }
        }));
        break; // Stop pipeline on failure
      }
    }
    setCurrentStage(null);
  };

  const downloadAll = () => {
    const combined = stages
      .filter(s => results[s]?.status === 'completed')
      .map(s => `# ${results[s].title}\n\n${results[s].content}\n\n---\n\n`)
      .join("");
    
    const blob = new Blob([combined], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SDD_${context.projectName.replace(/\s+/g, '_')}.md`;
    a.click();
  };

  return (
    <div className="flex flex-col h-screen max-h-[calc(100vh-120px)]">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold font-mono tracking-tighter text-blue-400">
            SYSTEM DESIGN ORCHESTRATOR <span className="text-neutral-600">v1.0</span>
          </h1>
          <p className="text-xs text-neutral-500 font-mono">PROJECT_ID: {context.projectName.toUpperCase().substring(0, 8)}</p>
        </div>
        <div className="flex gap-2">
           <button 
            onClick={onReset}
            className="px-4 py-2 border border-neutral-800 text-neutral-400 hover:bg-neutral-800 font-mono text-xs uppercase"
          >
            Reset
          </button>
          <button 
            onClick={runPipeline}
            disabled={!!currentStage}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs uppercase disabled:opacity-50"
          >
            Run Full Pipeline
          </button>
          <button 
            onClick={downloadAll}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white font-mono text-xs uppercase"
          >
            <Download size={14} className="inline mr-2" />
            Export SDD
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 flex-1 overflow-hidden">
        {/* Stages Sidebar */}
        <div className="col-span-3 border-r border-neutral-800 pr-4 overflow-y-auto custom-scrollbar">
          <div className="space-y-1">
            {stages.map((stage) => {
              const res = results[stage];
              const isActive = currentStage === stage;
              return (
                <button
                  key={stage}
                  onClick={() => res?.status === 'completed' && setSelectedResult(stage)}
                  disabled={!res}
                  className={cn(
                    "w-full text-left p-3 flex justify-between items-center transition-all border",
                    isActive ? "bg-blue-900/20 border-blue-500/50" : "border-transparent bg-neutral-900/30 hover:bg-neutral-800",
                    res?.status === 'completed' ? "cursor-pointer" : "cursor-default opacity-60"
                  )}
                >
                  <div className="flex items-center gap-3">
                    {res?.status === 'completed' ? (
                      <CheckCircle2 size={16} className="text-green-500" />
                    ) : res?.status === 'running' ? (
                      <Loader2 size={16} className="text-blue-500 animate-spin" />
                    ) : res?.status === 'failed' ? (
                      <AlertCircle size={16} className="text-red-500" />
                    ) : (
                      <Circle size={16} className="text-neutral-700" />
                    )}
                    <span className={cn(
                      "text-xs font-mono uppercase tracking-widest",
                      isActive ? "text-blue-400" : "text-neutral-400"
                    )}>
                      {STAGE_CONFIG[stage].title}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Area */}
        <div className="col-span-9 flex flex-col overflow-hidden">
          <div className="flex-1 bg-neutral-950 border border-neutral-800 rounded p-4 font-mono text-sm overflow-y-auto custom-scrollbar relative">
            <AnimatePresence mode="wait">
              {currentStage ? (
                <motion.div 
                  key="streaming"
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }} 
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center gap-2 text-blue-500 mb-4 border-b border-blue-900/50 pb-2">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="uppercase tracking-widest text-xs">Generating: {STAGE_CONFIG[currentStage].title}...</span>
                  </div>
                  <div className="text-neutral-300 whitespace-pre-wrap leading-relaxed">
                    {streamingText}
                  </div>
                </motion.div>
              ) : selectedResult ? (
                <motion.div 
                  key="selected"
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="prose prose-invert max-w-none prose-sm"
                >
                  <div className="flex items-center justify-between mb-6 sticky top-0 bg-neutral-950 py-2 border-b border-neutral-800">
                    <h2 className="text-lg font-bold text-white uppercase tracking-tighter m-0">
                      {STAGE_CONFIG[selectedResult as SDLCStage].title}
                    </h2>
                    <div className="text-[10px] text-neutral-500">
                      STATUS: OK | BYTES: {results[selectedResult].content.length}
                    </div>
                  </div>
                  <div className="text-neutral-300 whitespace-pre-wrap leading-relaxed">
                    {results[selectedResult].content}
                  </div>
                </motion.div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-neutral-600">
                  <FileText size={48} className="mb-4 opacity-20" />
                  <p className="text-xs uppercase tracking-widest">Select a completed stage to review output</p>
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
