
interface UserMessageContainerProps {
  userInput?: string;
}

export default function UserMessageContainer({ 
  userInput,
}: UserMessageContainerProps) {
  return (
    <div className="space-y-4">
      {userInput && (
        <div className="bg-gray-100 p-4 rounded-lg">
          <p className="font-medium">You:</p>
          <p>{userInput}</p>
        </div>
      )}
    </div>
  );
}