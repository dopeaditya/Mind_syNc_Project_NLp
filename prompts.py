# prompts.py

import sqlite3
from collections import Counter
import re
import random

# Re-using the STOP_WORDS from the insights feature for consistency
STOP_WORDS = [
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'he', 'him', 
    'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their', 'what', 'which', 'who', 'whom', 'this', 
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'to', 'from', 'in', 
    'out', 'on', 'off', 'so', 'then', 'too', 'very', 'can', 'will', 'just', 'don', 'should', 'now'
]

def generate_prompt():
    """
    Analyzes the last 7 days of entries and generates a context-aware prompt.
    """
    conn = sqlite3.connect('database/journal.db')
    cursor = conn.cursor()

    # Fetch entries from the last 7 days
    cursor.execute("SELECT text, mood, productivity FROM entries WHERE date >= date('now', '-7 days')")
    entries = cursor.fetchall()
    conn.close()

    if len(entries) < 3:
        return "What's on your mind today?" # Default prompt if not enough data

    # --- Rule 1: Analyze Productivity Trend ---
    # We'll compare the average productivity of the 3 most recent entries vs the 3 before them
    if len(entries) >= 6:
        recent_prod = sum(e[2] for e in entries[-3:]) / 3
        older_prod = sum(e[2] for e in entries[-6:-3]) / 3
        if recent_prod < older_prod - 0.15: # If productivity has dropped significantly
            return "It seems like focus has been a challenge lately. What is the single biggest obstacle you're facing right now?"

    # --- Rule 2: Find a Recurring Topic ---
    raw_text = ' '.join([entry[0] for entry in entries])
    clean_text = re.sub(r'[^\w\s]', '', raw_text).lower()
    words = [word for word in clean_text.split() if word not in STOP_WORDS]
    
    # Let's find a common two-word phrase
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    bigram_counts = Counter(bigrams)
    
    for phrase, count in bigram_counts.most_common(5):
        if count >= 2: # If a phrase was mentioned at least twice
            return f"You've mentioned '{phrase}' a few times this week. What is one aspect of it that you're proud of, and one that you're still thinking about?"

    # --- Rule 3: Check for High Mood but Low Productivity ---
    mood_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    avg_mood = sum(mood_map.get(e[1], 0) for e in entries) / len(entries)
    avg_prod = sum(e[2] for e in entries) / len(entries)
    
    if avg_mood > 0.3 and avg_prod < 0.4:
        return "You've been in good spirits, which is great! What might be a fun, low-pressure task you could complete today to build some momentum?"

    # --- Fallback Prompts ---
    # If no other rules match, pick a random general prompt
    general_prompts = [
        "What was the highlight of your day so far?",
        "Describe a challenge you faced recently and how you handled it.",
        "What's one thing you're looking forward to this week?",
        "Is there anything you've been avoiding? What's one small step you could take on it?",
    ]
    return random.choice(general_prompts)
