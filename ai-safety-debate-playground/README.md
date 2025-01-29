# AI Safety Debate Web Application

This project implements an AI debate system inspired by the paper ["AI Safety via Debate"](https://arxiv.org/abs/1805.00899) by Geoffrey Irving, Paul Christiano, and Dario Amodei. The application enables two AI agents to engage in a structured debate on a given topic, taking opposing positions and presenting arguments in alternating rounds.

## Features

- Real-time streaming of AI responses using Server-Sent Events (SSE)
- Interactive debate format with multiple rounds
- Clean, responsive UI built with React and Tailwind CSS
- Markdown support for formatted debate responses
- Backend powered by FastAPI and OpenAI's GPT-4

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ratcht/alignment
cd alignment/ai-safety-debate
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a .env file in the backend directory:
```
OPENAI_API_KEY=your_api_key_here
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd app/backend
uvicorn app:app --reload
```

2. Start the frontend development server:
```bash
cd app/frontend
npm run dev
```

3. Open http://localhost:3000 in your browser

## Project Structure

```
├── backend/
│   ├── app.py            # FastAPI server and debate generation logic
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── components/       # React components
│   ├── hooks/           # Custom React hooks
│   └── pages/           # Next.js pages
```

## How It Works

1. User submits a debate topic
2. Two AI debaters engage in alternating rounds of discussion
3. Each debater aims to make persuasive arguments while remaining open to agreement
4. The debate continues for 3 rounds by default

## Technical Implementation

- Uses Server-Sent Events for real-time streaming of AI responses
- Implements a custom stream handler for managing debate state
- Utilizes OpenAI's GPT-4 for generating coherent and contextual responses
- Employs React for a responsive and interactive UI

## Future Plans

- Configurable debate structure (with a YAML file)
- Add a reward system, where you can select the best response.
- - This would ideally allow for the debate to produce trainable data/improve model quality through RLHF
- Swappable LLMs (open-source models, etc.)
- More cool features (multiple debators, an AI judge, etc.)

```