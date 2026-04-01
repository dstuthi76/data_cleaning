# Synthetic code samples with known bugs and ground truth
TASKS = [
    # ── EASY: Bug Detection ──────────────────────────────────────────
    {
        "task_id": "task_easy",
        "code_snippet": """
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)  # Bug: crashes on empty list
""",
        "ground_truth": {
            "has_bug": True,
            "bug_type": "ZeroDivisionError",
            "bug_line": 5,
            "keywords": ["empty", "zerodivision", "division", "zero", "len", "guard", "check"]
        },
        "instructions": (
            "Analyze the code snippet. Call action_type='analyze' to describe "
            "whether it contains a bug. Then call action_type='done' when finished."
        )
    },
    # ── MEDIUM: Bug Fix ──────────────────────────────────────────────
    {
        "task_id": "task_medium",
        "code_snippet": """
def binary_search(arr, target):
    low, high = 0, len(arr)   # Bug: should be len(arr)-1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
        "ground_truth": {
            "has_bug": True,
            "bug_type": "IndexError",
            "bug_line": 2,
            "fix": "high = len(arr) - 1",
            "fix_keywords": ["len(arr) - 1", "len(arr)-1", "high = len"]
        },
        "instructions": (
            "Analyze the code for bugs using action_type='analyze', then provide "
            "the corrected code using action_type='fix'. Call action_type='done' when finished."
        )
    },
    # ── HARD: Full Code Review ───────────────────────────────────────
    {
        "task_id": "task_hard",
        "code_snippet": """
def process_user_data(data):
    results = []
    for i in range(len(data)):          # Issue 1: not Pythonic
        user = data[i]
        if user['age'] > 18:
            name = user['name'].upper() # Issue 2: no KeyError guard
            results.append({
                'name': name,
                'status': 'adult',
                'score': user['score'] * 1.5  # Issue 3: no type check
            })
    password = "hardcoded_secret_123"   # Issue 4: security — hardcoded secret
    return results
""",
        "ground_truth": {
            "issues": [
                {"type": "style", "keyword": "enumerate"},
                {"type": "safety", "keyword": "keyerror"},
                {"type": "safety", "keyword": "type"},
                {"type": "security", "keyword": "hardcoded"},
            ],
            "min_issues_expected": 2,   # must catch at least 2 of 4
            "quality_score_range": [1, 5]
        },
        "instructions": (
            "Perform a full code review. Use action_type='analyze' to list all bugs and issues, "
            "action_type='fix' to provide improved code, action_type='review' to give a summary "
            "quality rating (1–5) and overall assessment. Call action_type='done' when finished."
        )
    }
]