from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from env.environment import CodeReviewEnv
from env.models import Action, StepResult, StateResult, Observation

app = FastAPI(title="CodeReviewEnv", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Single global env instance (sufficient for hackathon)
env = CodeReviewEnv()

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task_easy"

class StepRequest(BaseModel):
    action_type: str
    content: str
    confidence: float = 1.0

@app.post("/reset", response_model=Observation)
def reset(req: ResetRequest = ResetRequest()):
    obs = env.reset(task_id=req.task_id)
    return obs

@app.post("/step", response_model=StepResult)
def step(req: StepRequest):
    if env.done:
        raise HTTPException(400, "Episode done — call /reset first")
    action = Action(
        action_type=req.action_type,
        content=req.content,
        confidence=req.confidence
    )
    return env.step(action)

@app.get("/state", response_model=StateResult)
def state():
    return env.state()

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"id": "task_easy",   "difficulty": "easy",   "name": "Bug Detection"},
            {"id": "task_medium", "difficulty": "medium",  "name": "Bug Fix"},
            {"id": "task_hard",   "difficulty": "hard",    "name": "Full Code Review"},
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}