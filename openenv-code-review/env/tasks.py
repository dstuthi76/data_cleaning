from env.data import TASKS
from env.models import Action, Reward
from typing import Dict, Any

def get_task(task_id: str) -> dict:
    for t in TASKS:
        if t["task_id"] == task_id:
            return t
    raise ValueError(f"Unknown task_id: {task_id}")

# ── EASY GRADER ──────────────────────────────────────────────────────────────
def grade_easy(history: list[str], action: Action, gt: dict) -> Reward:
    combined = " ".join(history + [action.content]).lower()
    score = 0.0
    breakdown = {}

    # Did agent identify there IS a bug?
    if "bug" in combined or "error" in combined or "crash" in combined:
        score += 0.4
        breakdown["bug_identified"] = 0.4

    # Did agent name the right error type?
    if gt["bug_type"].lower() in combined or "zero" in combined or "division" in combined:
        score += 0.3
        breakdown["correct_error_type"] = 0.3

    # Did agent mention a fix/guard?
    if any(k in combined for k in gt["keywords"]):
        score += 0.3
        breakdown["fix_suggested"] = 0.3

    return Reward(
        value=min(score, 1.0),
        breakdown=breakdown,
        message="Easy: Bug detection grader"
    )

# ── MEDIUM GRADER ────────────────────────────────────────────────────────────
def grade_medium(history: list[str], action: Action, gt: dict) -> Reward:
    combined = " ".join(history + [action.content]).lower()
    score = 0.0
    breakdown = {}

    has_fix_action = any("fix" in h.lower() for h in history) or action.action_type == "fix"

    if "bug" in combined or "error" in combined or "index" in combined:
        score += 0.25
        breakdown["bug_found"] = 0.25

    if gt["bug_type"].lower() in combined or "indexerror" in combined or "index error" in combined:
        score += 0.25
        breakdown["error_named"] = 0.25

    if has_fix_action and any(k in combined for k in gt["fix_keywords"]):
        score += 0.4
        breakdown["correct_fix"] = 0.4

    if has_fix_action:
        score += 0.1
        breakdown["attempted_fix"] = 0.1

    return Reward(
        value=min(score, 1.0),
        breakdown=breakdown,
        message="Medium: Bug fix grader"
    )

# ── HARD GRADER ──────────────────────────────────────────────────────────────
def grade_hard(history: list[str], action: Action, gt: dict) -> Reward:
    combined = " ".join(history + [action.content]).lower()
    score = 0.0
    breakdown = {}

    # Count issues caught
    issues_caught = sum(
        1 for issue in gt["issues"]
        if issue["keyword"] in combined
    )
    issue_ratio = min(issues_caught / len(gt["issues"]), 1.0)
    issue_score = issue_ratio * 0.5
    score += issue_score
    breakdown["issues_caught"] = round(issue_score, 3)

    # Did they provide a fix?
    if action.action_type == "fix" or "fix" in combined or "def process" in combined:
        score += 0.2
        breakdown["fix_provided"] = 0.2

    # Did they write a review summary?
    if action.action_type == "review" or any(
        w in combined for w in ["rating", "quality", "score", "overall", "recommend"]
    ):
        score += 0.2
        breakdown["review_written"] = 0.2

    # Security issue specifically caught?
    if "hardcoded" in combined or "secret" in combined or "password" in combined:
        score += 0.1
        breakdown["security_flagged"] = 0.1

    return Reward(
        value=min(score, 1.0),
        breakdown=breakdown,
        message="Hard: Full code review grader"
    )

GRADERS = {
    "task_easy": grade_easy,
    "task_medium": grade_medium,
    "task_hard": grade_hard,
}