import React from 'react';
import { ProjectContext } from '../types';
import { Terminal, Plus, Trash2 } from 'lucide-react';

interface Props {
  context: ProjectContext;
  setContext: (context: ProjectContext) => void;
  onStart: () => void;
}

export default function ContextForm({ context, setContext, onStart }: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setContext({ ...context, [name]: value });
  };

  const handleArrayChange = (name: keyof ProjectContext, index: number, value: string) => {
    const arr = [...(context[name] as string[])];
    arr[index] = value;
    setContext({ ...context, [name]: arr });
  };

  const addToArray = (name: keyof ProjectContext) => {
    const arr = [...(context[name] as string[])];
    arr.push("");
    setContext({ ...context, [name]: arr });
  };

  const removeFromArray = (name: keyof ProjectContext, index: number) => {
    const arr = [...(context[name] as string[])];
    arr.splice(index, 1);
    setContext({ ...context, [name]: arr });
  };

  return (
    <div className="space-y-8 pb-20">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Info */}
        <section className="space-y-4 p-6 border border-neutral-800 bg-neutral-900/50 rounded-lg">
          <h2 className="text-xl font-bold flex items-center gap-2 text-white">
            <Terminal size={18} /> Basic Info
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs uppercase text-neutral-500 font-bold mb-1">Project Name</label>
              <input
                type="text"
                name="projectName"
                value={context.projectName}
                onChange={handleChange}
                className="w-full bg-neutral-950 border border-neutral-800 p-2 text-neutral-200 outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs uppercase text-neutral-500 font-bold mb-1">Description</label>
              <textarea
                name="projectDescription"
                value={context.projectDescription}
                onChange={handleChange}
                className="w-full bg-neutral-950 border border-neutral-800 p-2 text-neutral-200 outline-none focus:border-blue-500 h-24"
              />
            </div>
            <div>
              <label className="block text-xs uppercase text-neutral-500 font-bold mb-1">Business Domain</label>
              <input
                type="text"
                name="businessDomain"
                value={context.businessDomain}
                onChange={handleChange}
                className="w-full bg-neutral-950 border border-neutral-800 p-2 text-neutral-200 outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </section>

        {/* Technical Context */}
        <section className="space-y-4 p-6 border border-neutral-800 bg-neutral-900/50 rounded-lg">
          <h2 className="text-xl font-bold flex items-center gap-2 text-white">
            <Terminal size={18} /> Tech Stack
          </h2>
          <div className="grid grid-cols-1 gap-4">
             <div>
              <label className="block text-xs uppercase text-neutral-500 font-bold mb-1">Cloud Provider</label>
              <select 
                name="cloudProvider" 
                value={context.cloudProvider} 
                onChange={handleChange}
                className="w-full bg-neutral-950 border border-neutral-800 p-2 text-neutral-200 outline-none focus:border-blue-500"
              >
                <option value="AWS">AWS</option>
                <option value="Azure">Azure</option>
                <option value="GCP">GCP</option>
                <option value="On-Premise">On-Premise</option>
              </select>
            </div>
            {/* Features Array */}
            <div>
              <label className="block text-xs uppercase text-neutral-500 font-bold mb-1 flex justify-between">
                Features
                <button onClick={() => addToArray('features')} className="text-blue-500 hover:text-blue-400">
                  <Plus size={14} />
                </button>
              </label>
              <div className="space-y-2 mt-2">
                {context.features.map((feature, i) => (
                  <div key={i} className="flex gap-2">
                    <input
                      type="text"
                      value={feature}
                      onChange={(e) => handleArrayChange('features', i, e.target.value)}
                      className="flex-1 bg-neutral-950 border border-neutral-800 p-1 text-sm text-neutral-200 outline-none focus:border-blue-500"
                    />
                    <button onClick={() => removeFromArray('features', i)} className="text-red-500 opacity-50 hover:opacity-100">
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Business Requirements */}
        <section className="md:col-span-2 space-y-4 p-6 border border-neutral-800 bg-neutral-900/50 rounded-lg">
           <h2 className="text-xl font-bold flex items-center gap-2 text-white">
            <Terminal size={18} /> Business Requirements
          </h2>
          <textarea
            name="businessRequirements"
            value={context.businessRequirements}
            onChange={handleChange}
            placeholder="Describe specific business rules, compliance needs, or constraints..."
            className="w-full bg-neutral-950 border border-neutral-800 p-3 text-neutral-200 outline-none focus:border-blue-500 h-32"
          />
        </section>
      </div>

      <div className="flex justify-center pt-8">
        <button
          onClick={onStart}
          className="px-12 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold uppercase tracking-widest transition-all rounded shadow-[0_0_20px_rgba(37,99,235,0.4)]"
        >
          Initialize SDLC Pipeline
        </button>
      </div>
    </div>
  );
}
