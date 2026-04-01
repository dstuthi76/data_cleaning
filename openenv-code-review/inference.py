#!/usr/bin/env python3
"""
Baseline inference script for CodeReviewEnv.
Reads API_BASE_URL, MODEL_NAME, HF_TOKEN from environment variables.
Runs all 3 tasks and reports scores.
"""
import os
import json
import httpx
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", os.environ.get("OPENAI_API_KEY", ""))
ENV_URL      = os.environ.get("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

TASK_IDS = ["task_easy", "task_medium", "task_hard"]

SYSTEM_PROMPT = """You are an expert code reviewer. You will be given a code snippet and instructions.
Use the available action types: analyze, fix, review, done.
Always respond in JSON format:
{"action_type": "...", "content": "...", "confidence": 0.0-1.0}
When finished, use action_type "done"."""

def env_reset(task_id: str) -> dict:
    r = httpx.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(action_type: str, content: str, confidence: float = 1.0) -> dict:
    r = httpx.post(f"{ENV_URL}/step",
                   json={"action_type": action_type, "content": content, "confidence": confidence},
                   timeout=30)
    r.raise_for_status()
    return r.json()

def run_episode(task_id: str) -> float:
    print(f"\n{'='*50}")
    print(f"Task: {task_id}")
    obs = env_reset(task_id)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Code to review:\n```python\n{obs['code_snippet']}\n```\n\n"
            f"Instructions: {obs['instructions']}"
        )}
    ]

    episode_score = 0.0
    max_steps = 6

    for step_num in range(max_steps):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=500,
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()

        # Parse JSON action
        try:
            clean = raw.strip("```json").strip("```").strip()
            action = json.loads(clean)
        except Exception:
            action = {"action_type": "analyze", "content": raw, "confidence": 0.5}

        print(f"  Step {step_num+1} | action={action.get('action_type')} | "
              f"content={action.get('content','')[:80]}...")

        result = env_step(
            action_type=action.get("action_type", "analyze"),
            content=action.get("content", raw),
            confidence=float(action.get("confidence", 1.0))
        )

        reward = result["reward"]["value"]
        episode_score = max(episode_score, reward)
        print(f"           reward={reward:.3f} | done={result['done']}")

        # Add assistant + env feedback to messages
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content":
            f"Reward: {reward:.3f}. Feedback: {result['observation']['feedback_history'][-1] if result['observation']['feedback_history'] else 'ok'}"
            + (" Task complete." if result["done"] else " Continue.")
        })

        if result["done"]:
            break

    print(f"  Final score for {task_id}: {episode_score:.3f}")
    return episode_score

def main():
    print("CodeReviewEnv Baseline Inference")
    print(f"Model: {MODEL_NAME} | Endpoint: {API_BASE_URL}")
    scores = {}
    for task_id in TASK_IDS:
        scores[task_id] = run_episode(task_id)

    print("\n" + "="*50)
    print("BASELINE RESULTS")
    print("="*50)
    for k, v in scores.items():
        print(f"  {k:<15} {v:.3f}")
    avg = sum(scores.values()) / len(scores)
    print(f"  {'AVERAGE':<15} {avg:.3f}")
    return scores

if __name__ == "__main__":
    main()