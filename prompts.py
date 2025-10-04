import sqlite3
import re
from collections import Counter, defaultdict
import random

# A more comprehensive list of words to ignore for better topic detection.
STOP_WORDS = [
    'a', 'about', 'am', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'being', 
    'but', 'by', 'can', 'did', 'do', 'does', 'doing', 'don', 'for', 'from', 
    'had', 'has', 'have', 'having', 'he', 'her', 'him', 'his', 'i', 'if', 'in', 
    'is', 'it', 'its', 'just', 'me', 'my', 'myself', 'now', 'of', 'off', 'on', 
    'or', 'our', 'ours', 's', 'she', 'should', 'so', 't', 'that', 'the', 'their', 
    'them', 'then', 'these', 'they', 'this', 'those', 'to', 'too', 'was', 'we', 
    'were', 'what', 'which', 'who', 'whom', 'will', 'with', 'you', 'your', 'yours'
]

def find_phrases(text, phrase_length=2):
    # This helper function remains the same.
    words = text.split()
    if len(words) < phrase_length: return []
    return [' '.join(words[i:i+phrase_length]) for i in range(len(words) - phrase_length + 1)]

def generate_prompt():
    """
    Generates a highly varied and relevant prompt using a multi-layered AI-like analysis.
    """
    conn = sqlite3.connect('database/journal.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT text, mood, productivity FROM entries ORDER BY id DESC LIMIT 30")
    recent_entries = cursor.fetchall()
    
    # --- LAYER 3: THE COACH (Expanded list for guaranteed variety) ---
    encouraging_thoughts = [
        "What is one small thing you can do today that your future self will thank you for?",
        "Think of a challenge you overcame. What strength did you discover in yourself?",
        "What's a simple pleasure you are grateful for today?",
        "Today is a new opportunity to move closer to your goals.",
        "Celebrate your progress, no matter how small it may seem.",
        "What is one thing you are genuinely curious about right now?",
        "Describe a small moment today that made you smile.",
        "What is one positive change, no matter how minor, you could make tomorrow?",
        "If you had an extra hour today, how would you spend it to recharge?",
        "What's one thing you're looking forward to in the coming week?",
        "Who is someone you could reach out to today to share a positive thought?",
        "What's a skill you have that you are proud of?",
        "Reflect on a past success. What key lesson can you apply to a current challenge?"
    ]

    if not recent_entries:
        conn.close()
        return random.choice(encouraging_thoughts)

    possible_prompts = list(encouraging_thoughts)

    # --- LAYER 1: THE AI ANALYST (Analyze the single most recent entry) ---
    last_entry_text, last_entry_mood, _ = recent_entries[0]
    clean_last_entry = re.sub(r'[^\w\s]', '', last_entry_text).lower()

    # Pattern matching to simulate AI understanding
    if any(word in clean_last_entry for word in ['problem', 'issue', 'struggle', 'fix', 'solve']):
        possible_prompts.append("It sounds like you're in problem-solving mode. What's the very first step you can take to address this challenge?")
    elif any(word in clean_last_entry for word in ['tomorrow', 'next', 'plan', 'will', 'going to']):
        possible_prompts.append("You seem to be thinking about the future. What is your main priority for tomorrow?")
    elif any(word in clean_last_entry for word in ['finished', 'completed', 'was', 'did', 'yesterday']):
        possible_prompts.append("Reflecting on recent events is powerful. What is the most important lesson you learned from yesterday?")

    # --- LAYER 2: THE HISTORIAN (Analyze historical trends) ---
    if len(recent_entries) > 2:
        all_text = ' '.join([entry[0] for entry in recent_entries])
        clean_text = re.sub(r'[^\w\s]', '', all_text).lower()
        phrases = find_phrases(clean_text, 2)
        
        if phrases:
            phrase_counts = Counter(phrases)
            for topic, count in phrase_counts.most_common(5):
                if count < 2: continue
                word1, word2 = topic.split()
                if word1 in STOP_WORDS and word2 in STOP_WORDS: continue

                topic_entries = [entry for entry in recent_entries if topic in entry[0].lower()]
                mood_map = {'positive': 1, 'neutral': 0, 'negative': -1}
                avg_mood = sum(mood_map.get(entry[1], 0) for entry in topic_entries) / len(topic_entries)

                if avg_mood > 0.2:
                    prompt = f"The topic of '{topic}' has been a positive one for you. How can you bring more of that energy into other parts of your life?"
                elif avg_mood < -0.2:
                    prompt = f"'{topic}' seems to have been a recurring challenge. What is one thing you can control about this situation?"
                else:
                    prompt = f"'{topic}' has been a consistent theme. What is your next intended step regarding this?"
                
                possible_prompts.append(prompt)

    conn.close()
    # The final selection from our large, diverse pool of prompts
    return random.choice(possible_prompts)

