from openai import OpenAI
from typing import List, Dict, AsyncGenerator
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from datetime import datetime
from pathlib import Path
from models import DebateRequest, DebateConfig, DebateResult
import aiofiles

load_dotenv()

# Initialize the data directory for storing results
DATA_DIR = Path("data")
RESULTS_DIR = DATA_DIR / "debate_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class DebateGenerator:
    def __init__(self, debate_id: str, config: DebateConfig):
        self.debate_id = debate_id
        self.config = config
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.topic_statement = ""
        self.debate_history = []

    async def generate_prompt(self, prompt: str, context: list[dict]):
        try:
            stream = self.client.chat.completions.create(
                model="gpt-4",
                messages=[*context, {"role": "user", "content": prompt}],
                stream=True,
                max_tokens=self.config.maxTokensPerResponse,
                temperature=self.config.temperature,
                presence_penalty=0.6,
                frequency_penalty=0.6,
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
                    
            if collected_message:
                yield {
                    "message": "",
                    "type": "token_end"
                }
                    
        except Exception as e:
            print(f"Error in generate_prompt: {str(e)}")
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
                await asyncio.sleep(0.01)
                    
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
            
            for debater_num in range(self.config.numDebaters):
                system_prompt = self.config.systemPrompts[debater_num]
                context = [{
                    "role": "system",
                    "content": system_prompt.content
                }]
                
                prompt = f"{self.topic_statement}\nPresent your argument for round {round_num + 1} as Debater {debater_num + 1}. Consider previous arguments and develop the discussion."
                
                response = ""
                async for token in self.generate_message(prompt, context, debater_num + 1):
                    if token["type"] == "token":
                        response += token["message"]
                    yield token
                    await asyncio.sleep(0.01)

                self.debate_history.append(response)
                self.topic_statement += f"Debater {debater_num + 1}: {response}\n"

                if debater_num < self.config.numDebaters - 1:
                    await asyncio.sleep(0.5)

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

async def generate_debate(prompt: str, config: DebateConfig, debate_id: str):
    try:
        debate_gen = DebateGenerator(debate_id, config)
        debate_gen.topic_statement = f"Debate topic: {prompt}\n\n"

        print(f"Starting debate {debate_id}")
        yield json.dumps({
            "type": "start_debate",
            "message": "Starting debate"
        })

        for i in range(config.numRounds):
            print(f"Starting round {i + 1}")
            async for item in debate_gen.generate_round(i):
                yield json.dumps(item)
                await asyncio.sleep(0.01)
            await asyncio.sleep(0.5)

        print(f"Debate {debate_id} complete")
        yield json.dumps({
            "type": "debate_complete",
            "message": "Debate complete"
        })
    except Exception as e:
        print(f"Error in generate_debate: {str(e)}")
        yield json.dumps({
            "type": "error",
            "message": "Error in debate generation"
        })

async def store_debate_result(result: DebateResult):
    """
    Stores the debate result in JSON format and updates the index file.
    Each debate gets its own JSON file, and we maintain an index for easy querying.
    """
    print("Store debate results")
    try:
        # Create a filename using timestamp and debate ID
        date_str = datetime.fromtimestamp(result.timestamp / 1000).strftime('%Y%m%d')
        filename = f"debate_{date_str}_{result.debateId}.json"
        
        # Store the complete debate result
        result_path = RESULTS_DIR / filename
        async with aiofiles.open(result_path, 'w', encoding='utf-8') as f:
            await f.write(result.model_dump_json(indent=2))
        
        # Update the index file with summary information
        index_path = RESULTS_DIR / "debate_index.jsonl"
        summary = {
            "debateId": result.debateId,
            "topic": result.topic,
            "timestamp": result.timestamp,
            "numDebaters": len(result.scores),
            "winner": result.finalRanking[0],
            "filename": filename,
            # Calculate average scores for quick reference
            "averageScores": {
                category: sum(score.scores[category] for score in result.scores) / len(result.scores)
                for category in result.scores[0].scores
            }
        }
        
        async with aiofiles.open(index_path, 'a', encoding='utf-8') as f:
            await f.write(json.dumps(summary) + '\n')
            
        return True
    except Exception as e:
        print(f"Error storing debate result: {str(e)}")
        return False

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
async def start_debate(request: DebateRequest):
    """Starts a new debate with the given configuration"""
    debate_id = str(len(debates) + 1)
    debates[debate_id] = {
        "prompt": request.prompt,
        "config": request.config
    }
    return {"debate_id": debate_id}

@app.get("/stream/{debate_id}")
async def stream(debate_id: str):
    """Streams the debate responses using server-sent events"""
    if debate_id not in debates:
        return {"error": "Debate not found"}
    
    debate_data = debates[debate_id]
    generator = generate_debate(
        debate_data["prompt"],
        debate_data["config"],
        debate_id=debate_id
    )
    return EventSourceResponse(generator)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)