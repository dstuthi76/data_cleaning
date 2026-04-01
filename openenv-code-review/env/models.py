from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class Observation(BaseModel):
    code_snippet: str
    task_id: str
    instructions: str
    step_count: int = 0
    feedback_history: List[str] = []

class Action(BaseModel):
    action_type: str = Field(..., description="One of: analyze, fix, review, done")
    content: str = Field(..., description="The agent's response content")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class Reward(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0)
    breakdown: Dict[str, float] = {}
    message: str = ""

class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any] = {}

class StateResult(BaseModel):
    task_id: str
    step_count: int
    episode_done: bool
    current_score: float
    code_snippet: str