import re

def custom_productivity_score(text):
    text = text.lower()
    productivity_keywords = [
        'complete', 'completed', 'finished', 'done', 'achieved', 'accomplished', 'organized',
        'planned', 'worked', 'progress', 'improve', 'improved', 'fixed', 'solved', 'resolved',
        'created', 'built', 'started', 'developed', 'designed', 'reviewed', 'prepared', 'submitted'
    ]
    keyword_count = sum(text.count(word) for word in productivity_keywords)
    words = re.findall(r'\w+', text)
    word_count = len(words)
    if word_count == 0:
        return 0.0
    keyword_density = keyword_count / word_count
    length_bonus = min(word_count / 100, 0.3)
    score = min(keyword_density + length_bonus, 1.0)
    return round(score, 3)
