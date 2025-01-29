// Core debate types
export interface Message {
  id: number;
  response: string;
  isComplete: boolean;
}

export interface MessageGroup {
  id: number;
  messages: Message[];
  isComplete?: boolean;

}

export interface DebateGroup {
  id: number;
  userInput: string;
  rounds: MessageGroup[];
  config: DebateConfig;  // Added this line
  isComplete: boolean;
}

// Configuration types
export interface SystemPrompt {
  role: string;
  content: string;
}

export interface DebateConfig {
  numRounds: number;
  numDebaters: number;
  temperature: number;
  maxTokensPerResponse: number;
  systemPrompts: SystemPrompt[];
  debateStyle: string;
}


// Component props
export interface ConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  config: DebateConfig;
  onSave: (config: DebateConfig) => void;
}


// Other constants and templates
export const DEFAULT_CONFIG: DebateConfig = {
  numRounds: 3,
  numDebaters: 2,
  temperature: 0.7,
  maxTokensPerResponse: 500,
  systemPrompts: [
    {
      role: "debater_1",
      content: "You are Debater 1. Support your position. Keep your arguments quite short. Goal: Convince the Judge of your side, even if it means agreeing."
    },
    {
      role: "debater_2",
      content: "You are Debater 2. Counter the previous argument and support your position."
    }
  ],
  debateStyle: "formal"
};

export const PROMPT_TEMPLATES = {
  formal: {
    debater_1: "You are Debater 1. Present logical arguments supported by evidence. Maintain professional tone. Focus on facts and reasoning.",
    debater_2: "You are Debater 2. Analyze and respond to previous arguments with counter-evidence. Maintain academic rigor."
  },
  socratic: {
    debater_1: "You are Debater 1. Use Socratic questioning to explore the topic. Focus on uncovering assumptions and implications.",
    debater_2: "You are Debater 2. Challenge premises through careful questioning. Seek deeper understanding."
  },
  collaborative: {
    debater_1: "You are Debater 1. Build on previous points while adding new perspectives. Seek common ground.",
    debater_2: "You are Debater 2. Synthesize arguments and find areas of agreement while exploring nuances."
  }
};