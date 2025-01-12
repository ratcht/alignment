import MarkdownDisplay from './MarkdownDisplay';

interface MessageContainerProps {
  message: {
    response: string;
  };
  isUserMessage?: boolean;
  userInput?: string;
  isStreaming: boolean;
}

export default function MessageContainer({ 
  message, 
  isUserMessage = false,
  userInput,
  isStreaming 
}: MessageContainerProps) {
  return (
    <div className="space-y-4">
      {isUserMessage && userInput && (
        <div className="bg-gray-100 p-4 rounded-lg">
          <p className="font-medium">You:</p>
          <p>{userInput}</p>
        </div>
      )}
      <div className="border rounded-lg p-6 bg-white">
        <MarkdownDisplay 
          content={message.response} 
          isStreaming={isStreaming} 
        />
      </div>
    </div>
  );
}