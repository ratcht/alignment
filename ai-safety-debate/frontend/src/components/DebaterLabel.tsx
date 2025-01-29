import React from 'react';

interface DebaterLabelProps {
  name: string;
  position: number;
  type: 'ai' | 'user';
}

export default function DebaterLabel({ name, position, type }: DebaterLabelProps) {
  const getBackgroundColor = () => {
    if (type === 'user') return 'bg-gray-700';
    // Alternate colors for AI debaters
    return position % 2 === 0 
      ? 'bg-gradient-to-r from-indigo-500 to-blue-600'
      : 'bg-gradient-to-r from-purple-500 to-indigo-600';
  };

  return (
    <div className="flex items-center gap-2 mb-3">
      <div className={`h-8 w-8 rounded-full ${getBackgroundColor()} flex items-center justify-center flex-shrink-0`}>
        {type === 'user' ? (
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        )}
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-medium text-gray-600">{name}</span>
        {type === 'ai' && (
          <span className="text-xs text-gray-400">AI Debater #{position}</span>
        )}
      </div>
    </div>
  );
}