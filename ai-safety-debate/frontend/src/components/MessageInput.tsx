import type { MessageInputProps } from '@/types/types';

export default function MessageInput({ 
  input, 
  isStreaming, 
  onInputChange, 
  onSubmit 
}: MessageInputProps) {
  return (
    <form onSubmit={onSubmit} className="relative">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => onInputChange(e.target.value)}
          className="flex-1 px-4 py-3 border border-gray-200 rounded-lg shadow-sm
                   focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                   placeholder:text-gray-400 text-gray-800
                   disabled:bg-gray-50 disabled:text-gray-500"
          placeholder={isStreaming ? "Processing..." : "Start a new debate topic..."}
          disabled={isStreaming}
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium
                   hover:bg-indigo-700 transition-colors duration-200
                   disabled:bg-gray-300 disabled:cursor-not-allowed
                   shadow-sm"
        >
          {isStreaming ? (
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Processing</span>
            </div>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </form>
  );
}