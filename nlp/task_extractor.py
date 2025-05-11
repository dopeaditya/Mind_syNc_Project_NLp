import re

def extract_tasks(text):
    task_patterns = [
        r"\b(?:need to|have to|must|should|want to|planning to|plan to|aim to|try to)\s+(.*?)(?:[.!\n]|$)",
        r"\b(?:to[- ]do|todo)[^\w]*(.*?)(?:[.!\n]|$)"
    ]
    tasks = []
    for pattern in task_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            task = match.strip().rstrip('.!')
            if task:
                tasks.append(task)
    return tasks
