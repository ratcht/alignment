interface FloatingButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export default function FloatingButton({ onClick, disabled }: FloatingButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="fixed bottom-6 right-6 w-12 h-12 flex items-center justify-center 
                 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 
                 disabled:bg-gray-400 transition-all duration-200"
      title="Reset conversation"
    >
      <svg
        className="w-6 h-6"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
        />
      </svg>
    </button>
  );
}