import DebaterLabel from './DebaterLabel';

export interface UserMessageContainerProps {
  userInput: string | undefined;
}


export default function UserMessageContainer({ userInput }: UserMessageContainerProps) {
  if (!userInput) return null;
  
  return (
    <div className="space-y-2">
      <DebaterLabel 
        name="You"
        position={0}
        type="user"
      />
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6 border border-gray-200">
        <p className="text-gray-800">{userInput}</p>
      </div>
    </div>
  );
}