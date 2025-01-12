interface MessageInputProps {
  input: string;
  isStreaming: boolean;
  onInputChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export default function MessageInput({ 
  input, 
  isStreaming, 
  onInputChange, 
  onSubmit 
}: MessageInputProps) {
  return (
    <form onSubmit={onSubmit} className="mb-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          className="flex-1 px-3 py-2 border rounded"
          placeholder={isStreaming ? "Processing..." : "Type a message..."}
          disabled={isStreaming}
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 
                   disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </form>
  );
}