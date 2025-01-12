from openai import OpenAI
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

def simulate_debate(topic: str, num_rounds: int = 3) -> List[Dict[str, str]]:
  """
  Simulate a debate between two AI debaters on a given topic.
  
  Args:
    topic (str): The debate topic
    num_rounds (int): Number of debate rounds
  
  Returns:
    List[Dict[str, str]]: List of debate exchanges
  """
  # Initialize OpenAI client (make sure to set your API key in environment variables)
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
  
  debate_history = []
  context = f"Debate topic: {topic}\n\n"
  
  for round in range(num_rounds):
    # First debater's turn
    print(f"\nRound {round}:")

    debater1_response = client.chat.completions.create(
      model="gpt-4",
      messages=[{
        "role": "system",
        "content": "You are Debater 1. Support your position."
      }, {
        "role": "user",
        "content": f"{context}\nPresent your argument for round {round + 1}."
      }]
    )
    
    debater1_argument = debater1_response.choices[0].message.content
    context += f"Debater 1: {debater1_argument}\n"

    print(f"Debater 1: {debater1_argument}\n")

    
    # Second debater's turn
    debater2_response = client.chat.completions.create(
      model="gpt-4",
      messages=[{
        "role": "system",
        "content": "You are Debater 2. Counter the previous argument and support your position."
      }, {
        "role": "user",
        "content": f"{context}\nCounter the previous argument and support your position."
      }]
    )
    
    debater2_argument = debater2_response.choices[0].message.content
    context += f"Debater 2: {debater2_argument}\n"
    
    debate_history.append({
      "round": round + 1,
      "debater1": debater1_argument,
      "debater2": debater2_argument
    })

    print(f"Debater 2: {debater2_argument}")
  
  return debate_history


from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from typing import AsyncGenerator, List

class MessageGenerator:
  def __init__(self, stream_id: str):
    self.stream_id = stream_id
    self.markdown_tokens = [
      "##", " ", "Hello", "\n", "\n", 
      "This", " ", "is", " ", "a", " ", "markdown", " ", "message", "\n", "\n",
      "-", " ", "Hi", "!"
    ]

  async def yield_tokens(self) -> AsyncGenerator[dict, None]:
    """Generate tokens for a single message"""
    for token in self.markdown_tokens:
      await asyncio.sleep(0.05)
      yield {
        "message": token,
        "type": "token"
      }

  async def generate_message(self, message_num: int) -> AsyncGenerator[dict, None]:
    """Generate a complete message including start and complete events"""
    yield {
      "type": "message_start",
      "message": f"Response {message_num + 1}"
    }
    
    async for token in self.yield_tokens():
      yield token
        
    yield {
      "type": "message_complete",
      "message": f"Message {message_num + 1} complete"
    }

async def stream_wrapper(generator: AsyncGenerator[dict, None]) -> AsyncGenerator[str, None]:
  """Wrap any generator with start and complete events"""
  yield json.dumps({
    "type": "start_batch",
    "message": "Starting responses"
  })

  async for item in generator:
    yield json.dumps(item)

  yield json.dumps({
    "type": "batch_complete",
    "message": "All responses complete"
  })

async def generate_multiple_responses(message: str, stream_id: str) -> AsyncGenerator[str, None]:
  """Main generator function that orchestrates the response generation"""
  message_gen = MessageGenerator(stream_id)
  
  async def generate_all_messages():
    for i in range(3):  # Generate 3 messages
      async for item in message_gen.generate_message(i):
        yield item
      await asyncio.sleep(0.5)  # Pause between messages
  
  async for response in stream_wrapper(generate_all_messages()):
    yield response

# FastAPI setup and routes
app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

active_streams = {}

@app.post("/start-stream")
async def start_stream(message: str = Body(..., embed=True)):
  stream_id = str(len(active_streams) + 1)
  active_streams[stream_id] = message
  return {"stream_id": stream_id}

@app.get("/stream/{stream_id}")
async def stream(stream_id: str):
  if stream_id not in active_streams:
    return {"error": "Stream not found"}
  message = active_streams[stream_id]
  response = generate_multiple_responses(message, stream_id)
  return EventSourceResponse(response)



# Example usage:
if __name__ == "__main__":
  topic = "Is the Earth round? Give very short and concise responses. Make sure you call out any errors in the opponent's response. Do anything you must to win the debate and give what you consider to be the best answer."
  debate_results = simulate_debate(topic, num_rounds=2)
