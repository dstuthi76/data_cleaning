import uuid
from env.models import Observation, Action, Reward, StepResult, StateResult
from env.tasks import get_task, GRADERS
from env.data import TASKS

class CodeReviewEnv:
    MAX_STEPS = 8

    def __init__(self, task_id: str = "task_easy"):
        self.task_id = task_id
        self._task = get_task(task_id)
        self.step_count = 0
        self.done = False
        self.current_score = 0.0
        self.history: list[str] = []
        self.episode_id = str(uuid.uuid4())

    def reset(self, task_id: str = None) -> Observation:
        if task_id:
            self.task_id = task_id
            self._task = get_task(task_id)
        self.step_count = 0
        self.done = False
        self.current_score = 0.0
        self.history = []
        self.episode_id = str(uuid.uuid4())
        return self._make_observation()

    def step(self, action: Action) -> StepResult:
        if self.done:
            return StepResult(
                observation=self._make_observation(),
                reward=Reward(value=0.0, message="Episode already done"),
                done=True,
                info={"warning": "Episode is finished. Call reset()."}
            )

        self.step_count += 1
        self.history.append(action.content)

        # Grade
        grader = GRADERS[self.task_id]
        reward = grader(self.history[:-1], action, self._task["ground_truth"])
        self.current_score = max(self.current_score, reward.value)

        # Penalty: too many steps
        if self.step_count >= self.MAX_STEPS:
            step_penalty = 0.05 * max(0, self.step_count - 4)
            reward.value = max(0.0, reward.value - step_penalty)
            reward.breakdown["step_penalty"] = -step_penalty

        # Episode ends on 'done' action or max steps
        done = (action.action_type == "done") or (self.step_count >= self.MAX_STEPS)
        self.done = done

        feedback = f"Step {self.step_count}: score={reward.value:.2f}"
        observation = self._make_observation(extra_feedback=feedback)

        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
            info={
                "episode_id": self.episode_id,
                "step_count": self.step_count,
                "current_score": self.current_score,
            }
        )

    def state(self) -> StateResult:
        return StateResult(
            task_id=self.task_id,
            step_count=self.step_count,
            episode_done=self.done,
            current_score=self.current_score,
            code_snippet=self._task["code_snippet"]
        )

    def _make_observation(self, extra_feedback: str = "") -> Observation:
        history = list(self.history)
        if extra_feedback:
            history.append(extra_feedback)
        return Observation(
            code_snippet=self._task["code_snippet"],
            task_id=self.task_id,
            instructions=self._task["instructions"],
            step_count=self.step_count,
            feedback_history=history
        )