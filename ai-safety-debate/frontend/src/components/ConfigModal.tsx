import { useState, useEffect } from 'react';
import type { ConfigModalProps, DebateConfig, SystemPrompt } from '@/types/types';
import { PROMPT_TEMPLATES } from '@/types/types';

export default function ConfigModal({ isOpen, onClose, config, onSave }: ConfigModalProps) {
  const [localConfig, setLocalConfig] = useState<DebateConfig>(config);
  
  // Reset local config when modal opens with new config
  useEffect(() => {
    setLocalConfig(config);
  }, [config]);

  if (!isOpen) return null;

  const handleStyleChange = (style: string) => {
    const templates = PROMPT_TEMPLATES[style as keyof typeof PROMPT_TEMPLATES];
    const newPrompts: SystemPrompt[] = [];
    
    for (let i = 0; i < localConfig.numDebaters; i++) {
      const roleKey = `debater_${i + 1}` as keyof typeof templates;
      newPrompts.push({
        role: `debater_${i + 1}`,
        content: templates[roleKey] || `You are Debater ${i + 1}. Present your arguments clearly.`
      });
    }

    setLocalConfig(prev => ({
      ...prev,
      systemPrompts: newPrompts,
      debateStyle: style
    }));
  };

  const handleNumDebatersChange = (value: string) => {
    const num = Math.max(2, Math.min(4, parseInt(value) || 2));
    const newPrompts = [...localConfig.systemPrompts];
    
    if (num > newPrompts.length) {
      // Add new debaters
      for (let i = newPrompts.length; i < num; i++) {
        newPrompts.push({
          role: `debater_${i + 1}`,
          content: `You are Debater ${i + 1}. Present your arguments clearly.`
        });
      }
    } else {
      // Remove excess debaters
      newPrompts.splice(num);
    }

    setLocalConfig(prev => ({
      ...prev,
      numDebaters: num,
      systemPrompts: newPrompts
    }));
  };

  const handleNumberInput = (value: string, key: keyof DebateConfig, min: number, max: number) => {
    const num = Math.max(min, Math.min(max, parseInt(value) || min));
    setLocalConfig(prev => ({
      ...prev,
      [key]: num
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6">Debate Configuration</h2>
        
        <div className="space-y-6">
          {/* Basic Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Basic Settings</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Rounds
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={localConfig.numRounds.toString()}
                  onChange={e => handleNumberInput(e.target.value, 'numRounds', 1, 10)}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Debaters
                </label>
                <input
                  type="number"
                  min="2"
                  max="4"
                  value={localConfig.numDebaters.toString()}
                  onChange={e => handleNumDebatersChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Advanced Settings</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={localConfig.temperature.toString()}
                  onChange={e => setLocalConfig(prev => ({
                    ...prev,
                    temperature: parseFloat(e.target.value)
                  }))}
                  className="w-full"
                />
                <span className="text-sm text-gray-500">{localConfig.temperature.toFixed(1)}</span>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Tokens per Response
                </label>
                <input
                  type="number"
                  min="100"
                  max="2000"
                  step="100"
                  value={localConfig.maxTokensPerResponse.toString()}
                  onChange={e => handleNumberInput(e.target.value, 'maxTokensPerResponse', 100, 2000)}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Debate Style */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Debate Style</h3>
            <select
              value={localConfig.debateStyle}
              onChange={e => handleStyleChange(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="formal">Formal Academic</option>
              <option value="socratic">Socratic Dialogue</option>
              <option value="collaborative">Collaborative Discussion</option>
            </select>
          </div>

          {/* System Prompts */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">System Prompts</h3>
            {localConfig.systemPrompts.map((prompt, index) => (
              <div key={prompt.role} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Debater {index + 1}
                </label>
                <textarea
                  value={prompt.content}
                  onChange={e => {
                    const newPrompts = [...localConfig.systemPrompts];
                    newPrompts[index] = {
                      ...prompt,
                      content: e.target.value
                    };
                    setLocalConfig(prev => ({
                      ...prev,
                      systemPrompts: newPrompts
                    }));
                  }}
                  className="w-full px-3 py-2 border rounded-lg h-24"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              onSave(localConfig);
              onClose();
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg 
                     hover:bg-indigo-700 transition-colors"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}