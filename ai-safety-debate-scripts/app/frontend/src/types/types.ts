export interface Message {
  id: number;
  userMessage: string;
  response: string;
  isComplete: boolean;
}

export interface StreamData {
  message: string;
  type?: string;
}