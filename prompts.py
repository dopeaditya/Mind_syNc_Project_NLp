import sqlite3
import re
from collections import Counter, defaultdict
import random
import math

# A more comprehensive list of words to ignore for better topic detection.
STOP_WORDS = [
    'a', 'about', 'am', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'being', 'but', 
    'by', 'can', 'did', 'do', 'does', 'doing', 'don', 'for', 'from', 'had', 'has', 
    'have', 'having', 'he', 'her', 'him', 'his', 'i', 'if', 'in', 'is', 'it', 'its', 
    'just', 'me', 'my', 'myself', 'now', 'of', 'off', 'on', 'or', 'our', 'ours', 
    's', 'she', 'should', 'so', 't', 'that', 'the', 'their', 'them', 'then', 
    'these', 'they', 'this', 'those', 'to', 'too', 'was', 'we', 'were', 'what', 
    'which', 'who', 'whom', 'will', 'with', 'you', 'your', 'yours', 'it', 'was',
    'today', 'yesterday', 'tomorrow'
]

def find_phrases(text, phrase_length=2):
    # This helper function remains the same.
    words = text.split()
    if len(words) < phrase_length: return []
    return [' '.join(words[i:i+phrase_length]) for i in range(len(words) - phrase_length + 1)]

def get_top_tf_idf_phrases(docs):
    # Helper to find important phrases using TF-IDF
    tf_scores = []
    for doc in docs:
        doc_tf = Counter(find_phrases(doc, 2))
        for phrase, count in doc_tf.items():
            doc_tf[phrase] = count / len(doc.split())
        tf_scores.append(doc_tf)

    doc_count = len(docs)
    phrase_doc_counts = Counter()
    all_phrases = set(p for doc_tf in tf_scores for p in doc_tf)
    
    for phrase in all_phrases:
        for doc_tf in tf_scores:
            if phrase in doc_tf:
                phrase_doc_counts[phrase] += 1

    idf_scores = {phrase: math.log(doc_count / (1 + count)) for phrase, count in phrase_doc_counts.items()}
    
    tfidf_scores = Counter()
    for i, doc_tf in enumerate(tf_scores):
        for phrase, tf in doc_tf.items():
            tfidf_scores[phrase] += tf * idf_scores[phrase]
            
    return [phrase for phrase, score in tfidf_scores.most_common(5)]

def generate_prompt():
    """
    Generates a highly varied, intelligent, and positive prompt using a refined multi-layered analysis.
    """
    conn = sqlite3.connect('database/journal.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT text, mood FROM entries ORDER BY id DESC LIMIT 30")
    recent_entries = cursor.fetchall()
    
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
    all_docs = [re.sub(r'[^\w\s]', '', entry[0]).lower() for entry in recent_entries]

    # --- LAYER 1: Immediate reaction to the latest entry's main topic ---
    if len(all_docs) > 1:
        latest_entry_doc = all_docs[0]
        historical_docs = all_docs[1:]
        
        # Find phrases in the latest entry that are rare in older entries
        latest_phrases = set(p for p in find_phrases(latest_entry_doc, 2) if not any(w in STOP_WORDS for w in p.split()))
        historical_phrases = set(p for doc in historical_docs for p in find_phrases(doc, 2))
        
        unique_latest_phrases = latest_phrases - historical_phrases
        if unique_latest_phrases:
            topic = random.choice(list(unique_latest_phrases))
            possible_prompts.append(f"In your last entry, you mentioned '{topic}'. Could you explore that thought a bit more?")

    # --- LAYER 2: Analyze historical trends with better topic filtering ---
    if len(recent_entries) > 2:
        top_historical_phrases = get_top_tf_idf_phrases(all_docs)
        
        for topic in top_historical_phrases:
            word1, word2 = topic.split()
            if word1 in STOP_WORDS and word2 in STOP_WORDS: continue

            topic_entries = [entry for entry in recent_entries if topic in entry[0].lower()]
            if len(topic_entries) < 2: continue

            mood_map = {'positive': 1, 'neutral': 0, 'negative': -1}
            avg_mood = sum(mood_map.get(entry[1], 0) for entry in topic_entries) / len(topic_entries)

            if avg_mood > 0.2:
                prompt = f"The topic of '{topic}' seems to be a source of positivity for you. How can you cultivate more of that?"
            elif avg_mood < -0.2:
                prompt = f"Regarding '{topic}', which has been on your mind, what's one positive outcome you'd like to work towards?"
            else:
                prompt = f"'{topic}' has been a consistent theme. What is your next intended step regarding this?"
            
            possible_prompts.append(prompt)

    conn.close()
    return random.choice(possible_prompts)

