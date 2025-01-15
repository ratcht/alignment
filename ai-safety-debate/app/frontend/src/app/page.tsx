'use client';

import { useState } from 'react';
import MessageInput from '@/components/MessageInput';
import MessageContainer from '@/components/MessageContainer';
import UserMessageContainer from '@/components/UserMessageContainer';

import FloatingButton from '@/components/FloatingButton';
import { useStreamHandler } from '@/hooks/useStreamHandler';

interface Message {
  id: number;
  response: string;
  isComplete: boolean;
}

interface MessageGroup {
  id: number;
  messages: Message[];
}

interface DebateGroup {
  id: number;
  userInput: string;
  rounds: MessageGroup[];
}

export default function DebateStream() {
  const [input, setInput] = useState('');
  const [debateGroups, setDebateGroups] = useState<DebateGroup[]>([]);
  const [currentStreamId, setCurrentStreamId] = useState<number | null>(null);
  const { startStream } = useStreamHandler();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const groupId = Date.now();
    setDebateGroups(prev => [...prev, {
      id: groupId,
      userInput: input,
      rounds: []
    }]);
    
    setCurrentStreamId(groupId);
    try {
      await startStream(
        input,
        (updater) => setDebateGroups(prev => {
          const targetGroup = prev[prev.length - 1];
          if (!targetGroup) return prev;
          
          return prev.map(group => 
            group.id === targetGroup.id 
              ? { ...group, rounds: updater(group.rounds) }
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

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset the conversation?')) {
      setDebateGroups([]);
      setCurrentStreamId(null);
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-50">
      <main className="p-4 max-w-4xl mx-auto pb-24">
        <h1 className="text-2xl font-bold mb-4">AI Safety Debate</h1>

        <MessageInput
          input={input}
          isStreaming={currentStreamId !== null}
          onInputChange={setInput}
          onSubmit={handleSubmit}
        />

        <div className="space-y-8">
          {debateGroups.map((group) => (
            <div key={group.id} className="space-y-4 border-b pb-8">
              <h2 className="text-xl font-semibold">Debate Topic: {group.userInput}</h2>
              {group.rounds.map((round, roundIndex) => (
                <div key={round.id} className="space-y-4 ml-4">
                  <UserMessageContainer 
                    userInput={roundIndex === 0 ? group.userInput : undefined}
                  />
                  <h3 className="text-lg font-medium">Round {roundIndex + 1}</h3>
                  {round.messages.map((message) => (
                    <MessageContainer
                      key={message.id}
                      message={message}
                    />
                  ))}
                </div>
              ))}
            </div>
          ))}
        </div>

        <FloatingButton 
          onClick={handleReset} 
          disabled={debateGroups.length === 0 || currentStreamId !== null}
        />
      </main>
    </div>
  );
}