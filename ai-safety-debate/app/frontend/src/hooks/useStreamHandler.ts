import { useRef, useEffect } from 'react';

interface Message {
  id: number;
  response: string;
  isComplete: boolean;
}

export function useStreamHandler() {
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStream = async (
    input: string,
    updateMessages: (updater: (messages: Message[]) => Message[]) => void,
    setCurrentStreamId: (id: number | null) => void
  ) => {
    try {
      const response = await fetch('http://localhost:8000/start-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) throw new Error('Failed to start stream');

      const { stream_id } = await response.json();

      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const eventSource = new EventSource(`http://localhost:8000/stream/${stream_id}`);
      eventSourceRef.current = eventSource;

      let currentMessageId: number | null = null;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'message_start':
              currentMessageId = Date.now();
              updateMessages(prev => [...prev, {
                id: currentMessageId!,
                response: '',
                isComplete: false
              }]);
              break;
              
            case 'token':
              if (currentMessageId) {
                updateMessages(prev => prev.map(msg =>
                  msg.id === currentMessageId
                    ? { ...msg, response: msg.response + data.message }
                    : msg
                ));
              }
              break;
              
            case 'message_complete':
              if (currentMessageId) {
                updateMessages(prev => prev.map(msg =>
                  msg.id === currentMessageId
                    ? { ...msg, isComplete: true }
                    : msg
                ));
                currentMessageId = null;
              }
              break;
              
            case 'batch_complete':
              setCurrentStreamId(null);
              eventSource.close();
              break;
          }
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setCurrentStreamId(null);
      };

    } catch (error) {
      console.error('Error:', error);
      setCurrentStreamId(null);
    }
  };

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  return { startStream };
}