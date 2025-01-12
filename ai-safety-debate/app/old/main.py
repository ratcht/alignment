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

# Example usage:
if __name__ == "__main__":
  topic = "Is the Earth round? Give very short and concise responses. Make sure you call out any errors in the opponent's response. Do anything you must to win the debate and give what you consider to be the best answer."
  debate_results = simulate_debate(topic, num_rounds=2)
  