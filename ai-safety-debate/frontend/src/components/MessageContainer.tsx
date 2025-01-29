import MarkdownDisplay from './MarkdownDisplay';
import DebaterLabel from './DebaterLabel';
import { Message } from '@/types/types';

interface MessageContainerProps {
  key: number;
  message: Message;
  position: number;
}

export default function MessageContainer({ message, position }: MessageContainerProps) {
  return (
    <div className="space-y-2">
      <DebaterLabel 
        name={`GPT-4o ${position}`}
        position={position}
        type="ai"
      />
      <div className="rounded-lg p-6 bg-white border border-gray-100 shadow-sm
                    hover:shadow-md transition-shadow duration-200">
        <MarkdownDisplay content={message.response} />
      </div>
    </div>
  );
}