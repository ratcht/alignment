from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class SystemPrompt(BaseModel):
    role: str
    content: str

class DebateConfig(BaseModel):
    numRounds: int = Field(..., ge=1, le=10)
    numDebaters: int = Field(..., ge=2, le=4)
    temperature: float = Field(..., ge=0, le=1)
    maxTokensPerResponse: int = Field(..., ge=100, le=2000)
    systemPrompts: List[SystemPrompt]
    debateStyle: str

class DebateRequest(BaseModel):
    prompt: str
    config: DebateConfig

class Score(BaseModel):
    reasoning: int = Field(..., ge=1, le=10)
    evidence: int = Field(..., ge=1, le=10)
    clarity: int = Field(..., ge=1, le=10)
    persuasiveness: int = Field(..., ge=1, le=10)
    honesty: int = Field(..., ge=1, le=10)

class DebateScore(BaseModel):
    debaterId: str
    ranking: int
    scores: Score
    feedback: str

class DebateResult(BaseModel):
    debateId: str
    topic: str
    timestamp: int
    config: DebateConfig
    scores: List[DebateScore]
    finalRanking: List[str]
    judgeNotes: str

class Message(BaseModel):
    id: int
    response: str
    isComplete: bool
    debaterId: str

class MessageGroup(BaseModel):
    id: int
    messages: List[Message]

class DebateGroup(BaseModel):
    id: int
    userInput: str
    rounds: List[MessageGroup]
    config: DebateConfig
    isComplete: bool
    result: Optional[DebateResult] = None