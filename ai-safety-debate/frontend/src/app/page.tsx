'use client';

import { useEffect, useRef, useState } from 'react';
import MessageInput from '@/components/MessageInput';
import MessageContainer from '@/components/MessageContainer';
import UserMessageContainer from '@/components/UserMessageContainer';
import FloatingButton from '@/components/FloatingButton';
import Navbar from '@/components/Navbar';
import ConfigModal from '@/components/ConfigModal';
import { useStreamHandler } from '@/hooks/useStreamHandler';
import type { DebateGroup, MessageGroup, DebateConfig } from '@/types/types';
import { DEFAULT_CONFIG } from '@/types/types';

export default function DebateStream() {
  // Core state management
  const [input, setInput] = useState<string>('');
  const [debateGroups, setDebateGroups] = useState<DebateGroup[]>([]);
  const [currentStreamId, setCurrentStreamId] = useState<number | null>(null);
  
  // Configuration state
  const [isConfigOpen, setIsConfigOpen] = useState<boolean>(false);
  const [debateConfig, setDebateConfig] = useState<DebateConfig>(DEFAULT_CONFIG);
  
  const { startStream } = useStreamHandler();

  const isDebateComplete = (debateGroup: DebateGroup) => {
    const lastRound = debateGroup.rounds[debateGroup.rounds.length - 1];
    return Boolean(lastRound.isComplete)
  }


  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!input.trim()) return;

    const groupId = Date.now();
    const newDebateGroup: DebateGroup = {
      id: groupId,
      userInput: input,
      rounds: [],
      config: debateConfig,
      isComplete: false
    };

    setDebateGroups(prev => [...prev, newDebateGroup]);
    setCurrentStreamId(groupId);

    try {
      await startStream(
        input,
        debateConfig,
        (updater: (rounds: MessageGroup[]) => MessageGroup[]) => setDebateGroups(prev => {
          const targetGroup = prev[prev.length - 1];
          if (!targetGroup) return prev;
          
          const updatedGroup = {
            ...targetGroup,
            rounds: updater(targetGroup.rounds)
          };

          // Check if debate is complete
          const complete = isDebateComplete(updatedGroup);
          
          return prev.map(group => 
            group.id === targetGroup.id 
              ? { ...updatedGroup, isComplete: complete }
              : group
          );
        }),
        setCurrentStreamId
      );
    } catch (error) {
      console.error('Stream error:', error);
      setCurrentStreamId(null);
    }
    setInput('');
  };

  const handleReset = (): void => {
    if (window.confirm('Are you sure you want to reset the conversation?')) {
      setDebateGroups([]);
      setCurrentStreamId(null);
    }
  };

  const handleConfigSave = (newConfig: DebateConfig): void => {
    setDebateConfig(newConfig);
    setIsConfigOpen(false);
  };

  const currentDebateRef = useRef<HTMLDivElement | null>(null);

  // Add useEffect for scrolling
  useEffect(() => {
    if (currentStreamId) {
      const element = document.getElementById(`debate-${currentStreamId}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, [currentStreamId, debateGroups]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <Navbar onOpenConfig={() => setIsConfigOpen(true)} />

      <ConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        config={debateConfig}
        onSave={handleConfigSave}
      />

      <main className="max-w-4xl mx-auto px-4 pt-24 pb-32">
        {/* <div className="mb-8">
          <MessageInput
            input={input}
            isStreaming={currentStreamId !== null}
            onInputChange={setInput}
            onSubmit={handleSubmit}
          />
        </div> */}

        <div className="space-y-12">
          {debateGroups.map((group) => (
            <div key={group.id}
                 id={`debate-${group.id}`} // Add ID for scrolling
                 className="bg-white rounded-xl shadow-lg p-6 space-y-6 border border-gray-100">
              <div className="pb-4 border-b border-gray-100">
                <span className="text-sm font-medium text-gray-500">Debate Topic</span>
                <h2 className="text-xl font-semibold text-gray-800 mt-1">
                  {group.userInput}
                </h2>
              </div>
              
              {group.rounds.map((round, roundIndex) => (
                <div key={round.id} className="space-y-6">
                  <UserMessageContainer 
                    userInput={roundIndex === 0 ? group.userInput : undefined}
                  />
                  <div className="flex items-center gap-2 mt-8 mb-4">
                    <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-semibold">
                      {roundIndex + 1}
                    </div>
                    <h3 className="text-xl font-medium text-gray-700">
                      Round {roundIndex + 1}
                    </h3>
                  </div>
                  {round.messages.map((message, messageIndex) => (
                    <MessageContainer
                      key={message.id}
                      message={message}
                      position={messageIndex + 1}
                    />
                  ))}
                </div>
              ))}

              {group.isComplete && (
                <p>Debate Complete!</p>
              )}              
            </div>
          ))}
        </div>
        </main>

        {/* Fixed chat bar at bottom */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto">
            <MessageInput
              input={input}
              isStreaming={currentStreamId !== null}
              onInputChange={setInput}
              onSubmit={handleSubmit}
            />
          </div>
        </div>

        <FloatingButton 
          onClick={handleReset} 
          disabled={debateGroups.length === 0 || currentStreamId !== null}
        />
      </div>
  );
}