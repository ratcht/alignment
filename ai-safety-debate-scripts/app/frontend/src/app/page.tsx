'use client';

import { useState } from 'react';
import MessageInput from '@/components/MessageInput';
import MessageContainer from '@/components/MessageContainer';
import FloatingButton from '@/components/FloatingButton';
import { useStreamHandler } from '@/hooks/useStreamHandler';

interface Message {
  id: number;
  response: string;
  isComplete: boolean;
}

interface MessageGroup {
  id: number;
  userInput: string;
  messages: Message[];
}

export default function TextStream() {
  const [input, setInput] = useState('');
  const [messageGroups, setMessageGroups] = useState<MessageGroup[]>([]);
  const [currentStreamId, setCurrentStreamId] = useState<number | null>(null);
  const { startStream } = useStreamHandler();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const groupId = Date.now();
    setMessageGroups(prev => [...prev, {
      id: groupId,
      userInput: input,
      messages: []
    }]);
    
    setCurrentStreamId(groupId);
    await startStream(
      input,
      (updater) => setMessageGroups(prev => {
        const targetGroup = prev[prev.length - 1];
        if (!targetGroup) return prev;
        
        return prev.map(group => 
          group.id === targetGroup.id 
            ? { ...group, messages: updater(group.messages) }
            : group
        );
      }),
      setCurrentStreamId
    );
    setInput('');
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset the conversation?')) {
      setMessageGroups([]);
      setCurrentStreamId(null);
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-50">
      <main className="p-4 max-w-4xl mx-auto pb-24">
        <h1 className="text-2xl font-bold mb-4">Markdown Stream</h1>

        <MessageInput
          input={input}
          isStreaming={currentStreamId !== null}
          onInputChange={setInput}
          onSubmit={handleSubmit}
        />

        <div className="space-y-8">
          {messageGroups.map((group) => (
            <div key={group.id} className="space-y-4">
              {group.messages.map((message, index) => (
                <MessageContainer
                  key={message.id}
                  message={message}
                  isUserMessage={index === 0}
                  userInput={index === 0 ? group.userInput : undefined}
                  isStreaming={!message.isComplete && currentStreamId === group.id}
                />
              ))}
            </div>
          ))}
        </div>

        <FloatingButton 
          onClick={handleReset} 
          disabled={messageGroups.length === 0 || currentStreamId !== null}
        />
      </main>
    </div>
  );
}