import { useRef, useEffect } from 'react';

interface Message {
  id: number;
  response: string;
  isComplete: boolean;
}

interface MessageGroup {
  id: number;
  messages: Message[];
}

export function useStreamHandler() {
  const eventSourceRef = useRef<EventSource | null>(null);
  const currentRoundRef = useRef<number | null>(null);
  const currentMessageRef = useRef<number | null>(null);

  const startStream = async (
    input: string,
    updateDebates: (updater: (rounds: MessageGroup[]) => MessageGroup[]) => void,
    setCurrentStreamId: (id: number | null) => void
  ) => {
    try {
      const response = await fetch('http://localhost:8000/start-debate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input }),
      });

      if (!response.ok) throw new Error('Failed to start stream');

      const { debate_id } = await response.json();

      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const eventSource = new EventSource(`http://localhost:8000/stream/${debate_id}`);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'start_debate':
              // Initialize the debate
              break;

            case 'round_start':
              // Start a new round
              currentRoundRef.current = Date.now();
              updateDebates(prev => [...prev, {
                id: currentRoundRef.current!,
                messages: []
              }]);
              break;

            case 'message_start':
              // Start a new message within the current round
              currentMessageRef.current = Date.now();
              updateDebates(prev => {
                const lastRound = prev[prev.length - 1];
                if (!lastRound) return prev;

                return prev.map(round =>
                  round.id === lastRound.id
                    ? {
                        ...round,
                        messages: [...round.messages, {
                          id: currentMessageRef.current!,
                          response: '',
                          isComplete: false
                        }]
                      }
                    : round
                );
              });
              break;
              
            case 'token':
              // Append token to the current message
              if (currentMessageRef.current) {
                updateDebates(prev => {
                  const lastRound = prev[prev.length - 1];
                  if (!lastRound) return prev;

                  return prev.map(round =>
                    round.id === lastRound.id
                      ? {
                          ...round,
                          messages: round.messages.map(msg =>
                            msg.id === currentMessageRef.current
                              ? { ...msg, response: msg.response + data.message }
                              : msg
                          )
                        }
                      : round
                  );
                });
              }
              break;
              
            case 'message_complete':
              // Mark the current message as complete
              if (currentMessageRef.current) {
                updateDebates(prev => {
                  const lastRound = prev[prev.length - 1];
                  if (!lastRound) return prev;

                  return prev.map(round =>
                    round.id === lastRound.id
                      ? {
                          ...round,
                          messages: round.messages.map(msg =>
                            msg.id === currentMessageRef.current
                              ? { ...msg, isComplete: true }
                              : msg
                          )
                        }
                      : round
                  );
                });
                currentMessageRef.current = null;
              }
              break;

            case 'round_complete':
              // Mark the current round as complete
              currentRoundRef.current = null;
              break;
              
            case 'debate_complete':
              setCurrentStreamId(null);
              eventSource.close();
              break;
          }
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
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