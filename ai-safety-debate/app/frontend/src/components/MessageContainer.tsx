import MarkdownDisplay from './MarkdownDisplay';

interface MessageContainerProps {
  message: {
    response: string;
  };
}

export default function MessageContainer({ 
  message, 
}: MessageContainerProps) {
  return (
    <div className="space-y-4">
      <div className="border rounded-lg p-6 bg-white">
        <MarkdownDisplay 
          content={message.response} 
        />
      </div>
    </div>
  );
}