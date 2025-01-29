from openai import OpenAI, AsyncOpenAI
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

class DebateGenerator:
  def __init__(self, debate_id: str):
    self.debate_id = debate_id
    self.markdown_tokens = [
      "##", " ", "Hello", "\n", "\n", 
      "This", " ", "is", " ", "a", " ", "markdown", " ", "message", "\n", "\n",
      "-", " ", "Hi", "!"
    ]
    self.client = OpenAI()
    self.topic_statement = ""
    self.debate_history = []

  async def yield_tokens(self) -> AsyncGenerator[dict, None]:
    """Generate tokens for a single message"""
    for token in self.markdown_tokens:
      await asyncio.sleep(0.05)
      yield {
        "message": token,
        "type": "token"
      }

  async def generate_prompt(self, prompt: str, context: list[dict]):
    print("Generating Prompt...")
    stream = self.client.chat.completions.create(
        model="gpt-4o",
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
      "message": f"Response {round_num + 1}"
    }
    
    # First debater's turn
    print(f"\nRound {round}:")
    print("Debator 1...")

    context = [{
        "role": "system",
        "content": "You are Debater 1. Support your position."
      }]
    prompt = f"{self.topic_statement}\nPresent your argument for round {round_num + 1}."
    
    response = ""

    async for token in self.generate_message(prompt, context, 1):
      response += token
      yield token

    self.debate_history.append(response)
    self.topic_statement += f"Debater 1: {self.debate_history[-1]}\n"

    
    # Second debater's turn
    print("Debator 2...")
    context = [{
        "role": "system",
        "content": "You are Debater 2. Counter the previous argument and support your position."
      }]
    prompt = f"{self.topic_statement}\nCounter the previous argument and support your position."
    response = ""
    async for token in self.generate_message(prompt, context, 2):
      response += token
      yield token
    
    self.debate_history.append(response)
    self.topic_statement += f"Debater 2: {self.debate_history[-1]}\n"

        
    yield {
      "type": "round_complete",
      "message": f"Message {round_num + 1} complete"
    }


  @classmethod
  async def debate_wrapper(cls, generator: AsyncGenerator[dict, None]) -> AsyncGenerator[str, None]:
    """Wrap any generator with start and complete events"""
    yield json.dumps({
      "type": "start_debate",
      "message": "Starting responses"
    })

    async for item in generator:
      yield json.dumps(item)

    yield json.dumps({
      "type": "debate_complete",
      "message": "All responses complete"
    })

async def generate_debate(prompt: str, num_rounds: int, debate_id: str) -> AsyncGenerator[str, None]:
  """Main generator function that orchestrates the debate generation"""
  debate_gen = DebateGenerator(debate_id)
  debate_gen.topic_statement = f"Debate topic: {prompt}\n\n"

  async def run_debate():
    for i in range(num_rounds):  # Generate 3 messages
      async for item in debate_gen.generate_round(i):
        yield item
      await asyncio.sleep(0.5)  # Pause between messages
  
  async for response in DebateGenerator.debate_wrapper(run_debate()):
    yield response
  
  # Dump message from active streams
  # streams.pop(stream_id)

# FastAPI setup and routes
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
async def start_stream(prompt: str = Body(..., embed=True)):
  debate_id = str(len(debates) + 1)
  debates[debate_id] = prompt
  return {"debate_id": debate_id}

@app.get("/stream/{debate_id}")
async def stream(debate_id: str):
  if debate_id not in debates:
    return {"error": "Debate not found"}
  message = debates[debate_id]
  response = generate_debate(message, debate_id)
  return EventSourceResponse(response)



# Example usage:
if __name__ == "__main__":
  topic = "Is the Earth round? Give very short and concise responses. Make sure you call out any errors in the opponent's response. Do anything you must to win the debate and give what you consider to be the best answer."
  debate_results = simulate_debate(topic, num_rounds=2)
