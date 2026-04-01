# CodeReviewEnv — OpenEnv Submission

An OpenEnv environment where AI agents perform real-world code review tasks:
detecting bugs, writing fixes, and producing quality assessments.

## Tasks
| ID | Difficulty | Task |
|----|-----------|------|
| task_easy | Easy | Detect if code has a bug |
| task_medium | Medium | Identify bug + provide fix |
| task_hard | Hard | Full review: bugs, improvements, quality rating |

## Action Space
| Field | Type | Values |
|-------|------|--------|
| action_type | string | analyze, fix, review, done |
| content | string | Agent's text response |
| confidence | float | 0.0–1.0 |

## Observation Space
| Field | Type | Description |
|-------|------|-------------|
| code_snippet | string | The code to review |
| task_id | string | Current task |
| instructions | string | What the agent must do |
| step_count | int | Steps taken |
| feedback_history | list | Prior feedback |

## Baseline Scores
| Task | Score |
|------|-------|
| task_easy | ~0.70 |
| task_medium | ~0.55 |
| task_hard | ~0.45 |

## Setup
```bash
pip install -r requirements.txt
uvicorn api.server:app --port 7860
```

## Run Inference
```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=sk-...
export ENV_URL=http://localhost:7860
python inference.py
```