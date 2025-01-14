from openai import OpenAI
from typing import List, Dict, AsyncGenerator
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

load_dotenv()

class DebateGenerator:
  def __init__(self, debate_id: str):
    self.debate_id = debate_id
    self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    self.topic_statement = ""
    self.debate_history = []

  async def generate_prompt(self, prompt: str, context: list[dict]):
    print("Generating Prompt...")
    stream = self.client.chat.completions.create(
      model="gpt-4",
      messages=[
        *context,
        {"role": "user", "content": prompt}
      ],
      stream=True,
    )
    for chunk in stream:
      if chunk.choices[0].delta.content is not None:
        yield {
          "message": chunk.choices[0].delta.content,
          "type": "token"
        }

  async def generate_message(self, message: str, context: list[dict], message_num: int) -> AsyncGenerator[dict, None]:
    """Generate a complete message including start and complete events"""
    yield {
      "type": "message_start",
      "message": f"Response {message_num + 1}"
    }
    
    async for token in self.generate_prompt(message, context):
      yield token
        
    yield {
      "type": "message_complete",
      "message": f"Message {message_num + 1} complete"
    }

  async def generate_round(self, round_num: int) -> AsyncGenerator[dict, None]:
    yield {
      "type": "round_start",
      "message": f"Round {round_num + 1}"
    }
    
    # First debater's turn
    print(f"\nRound {round_num + 1}:")
    print("Debater 1...")

    context = [{
      "role": "system",
      "content": "You are Debater 1. Support your position. Keep your arguments quite short. Goal: Convince the Judge of your side, even if it means agreeing."
    }] 
    prompt = f"{self.topic_statement}\nPresent your argument for round {round_num + 1}. Keep it quite short but make your arguments effective. Make it interesting. Goal: Convince the Judge of your side, even if it means agreeing."
    
    response = ""
    async for token in self.generate_message(prompt, context, 1):
      if token["type"] == "token":
        response += token["message"]
      yield token

    self.debate_history.append(response)
    self.topic_statement += f"Debater 1: {response}\n"

    # Second debater's turn
    print("Debater 2...")
    context = [{
      "role": "system",
      "content": "You are Debater 2. Counter the previous argument and support your position. Keep your arguments quite short. Goal: Convince the Judge of your side, even if it means agreeing."
    }]
    prompt = f"{self.topic_statement}\nCounter the previous argument and support your position. Keep it quite short but make your arguments effective. Make it interesting. Goal: Convince the Judge of your side, even if it means agreeing."
    
    response = ""
    async for token in self.generate_message(prompt, context, 2):
      if token["type"] == "token":
        response += token["message"]
      yield token
    
    self.debate_history.append(response)
    self.topic_statement += f"Debater 2: {response}\n"

    print(f"Debate History Len: {len(self.debate_history)}. Topic Statement Word Count: {len(self.topic_statement)}")
      
    yield {
      "type": "round_complete",
      "message": f"Round {round_num + 1} complete"
    }

  @classmethod
  async def debate_wrapper(cls, generator: AsyncGenerator[dict, None]) -> AsyncGenerator[str, None]:
    """Wrap debate with start and complete events"""
    yield json.dumps({
      "type": "start_debate",
      "message": "Starting debate"
    })

    async for item in generator:
      yield json.dumps(item)

    yield json.dumps({
      "type": "debate_complete",
      "message": "Debate complete"
    })

async def generate_debate(prompt: str, num_rounds: int, debate_id: str) -> AsyncGenerator[str, None]:
  """Main generator function that orchestrates the debate"""
  debate_gen = DebateGenerator(debate_id)
  debate_gen.topic_statement = f"Debate topic: {prompt}\n\n"

  async def run_debate():
    for i in range(num_rounds):
      async for item in debate_gen.generate_round(i):
        yield item
      await asyncio.sleep(0.5)  # Small pause between rounds
  
  async for response in DebateGenerator.debate_wrapper(run_debate()):
    yield response

# FastAPI setup
app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

debates = {}

@app.post("/start-debate")
async def start_debate(prompt: str = Body(..., embed=True)):
  debate_id = str(len(debates) + 1)
  debates[debate_id] = prompt
  return {"debate_id": debate_id}

@app.get("/stream/{debate_id}")
async def stream(debate_id: str):
  if debate_id not in debates:
    return {"error": "Debate not found"}
  prompt = debates[debate_id]
  generator = generate_debate(prompt, num_rounds=3, debate_id=debate_id)
  return EventSourceResponse(generator)

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)