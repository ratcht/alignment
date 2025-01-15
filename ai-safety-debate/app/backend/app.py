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
    try:
      stream = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[*context, {"role": "user", "content": prompt}],
        stream=True,
        max_tokens=500,  # Add a max token limit
        temperature=0.7,  # Add temperature for consistent responses
        presence_penalty=0.6,  # Encourage more focused responses
        frequency_penalty=0.6,  # Prevent repetition
      )
      
      collected_message = ""
      for chunk in stream:
        if chunk.choices[0].delta.content is not None:
          token = chunk.choices[0].delta.content
          collected_message += token
          yield {
            "message": token,
            "type": "token"
          }
          
      # Send a final confirmation token
      if collected_message:
        yield {
          "message": "",
          "type": "token_end"
        }
          
    except Exception as e:
      print(f"Error in generate_prompt: {str(e)}")
      # Send an error token that the frontend can handle
      yield {
        "message": "Error generating response",
        "type": "error"
      }

  async def generate_message(self, message: str, context: list[dict], message_num: int):
    try:
      yield {
        "type": "message_start",
        "message": f"Response {message_num + 1}"
      }
      
      async for token in self.generate_prompt(message, context):
        yield token
        await asyncio.sleep(0.01)  # Small delay to prevent overwhelming the connection
          
      yield {
        "type": "message_complete",
        "message": f"Message {message_num + 1} complete"
      }
        
    except Exception as e:
      print(f"Error in generate_message: {str(e)}")
      yield {
        "type": "error",
        "message": "Failed to generate message"
      }

  async def generate_round(self, round_num: int):
    try:
      yield {
        "type": "round_start",
        "message": f"Round {round_num + 1}"
      }
      
      # First debater's turn
      context = [{
        "role": "system",
        "content": "You are Debater 1. Support your position. Keep your arguments quite short. Goal: Convince the Judge of your side, even if it means agreeing."
      }]
      
      prompt = f"{self.topic_statement}\nPresent your argument for round {round_num + 1}. Keep it quite short but make your arguments effective."
      
      response = ""
      async for token in self.generate_message(prompt, context, 1):
        if token["type"] == "token":
          response += token["message"]
        yield token
        await asyncio.sleep(0.01)  # Prevent overwhelming the connection

      self.debate_history.append(response)
      self.topic_statement += f"Debater 1: {response}\n"

      # Add a small delay between debaters
      await asyncio.sleep(0.5)

      # Second debater's turn with similar pattern...
      context = [{
        "role": "system",
        "content": "You are Debater 2. Counter the previous argument and support your position."
      }]
      
      prompt = f"{self.topic_statement}\nCounter the previous argument and present your position."
      
      response = ""
      async for token in self.generate_message(prompt, context, 2):
        if token["type"] == "token":
          response += token["message"]
        yield token
        await asyncio.sleep(0.01)

      self.debate_history.append(response)
      self.topic_statement += f"Debater 2: {response}\n"

      yield {
        "type": "round_complete",
        "message": f"Round {round_num + 1} complete"
      }
        
    except Exception as e:
      print(f"Error in generate_round: {str(e)}")
      yield {
        "type": "error",
        "message": "Failed to complete round"
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
  print("in requirest")
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