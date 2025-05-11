
def productivity_score(text):
    keywords = ['completed', 'organized', 'productive', 'focus', 'achieved', 'goal']
    words = text.lower().split()
    score = sum(word in words for word in keywords)
    return min(score / 5, 1.0)
