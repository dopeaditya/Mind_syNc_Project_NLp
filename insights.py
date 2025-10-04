# insights.py

import sqlite3
from collections import Counter
import re

# A list of common words to ignore during analysis
STOP_WORDS = [
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
    'yours', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 
    'their', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 
    'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 
    'for', 'with', 'about', 'to', 'from', 'in', 'out', 'on', 'off', 'so', 
    'then', 'too', 'very', 'can', 'will', 'just', 'don', 'should', 'now', 's', 't'
]

def generate_insights(period="all"):
    """
    Connects to the database, analyzes entries for a specific period, 
    and returns a list of dictionaries with detailed insight data.
    """
    conn = sqlite3.connect('database/journal.db')
    cursor = conn.cursor()

    # Build the SQL query based on the requested period
    if period == "weekly":
        query = "SELECT text, mood, productivity FROM entries WHERE date >= date('now', '-7 days')"
    elif period == "monthly":
        query = "SELECT text, mood, productivity FROM entries WHERE date >= date('now', '-30 days')"
    else:
        query = "SELECT text, mood, productivity FROM entries"
        
    cursor.execute(query)
    entries = cursor.fetchall()
    conn.close()

    if not entries:
        return [] # Return an empty list if no entries

    # Clean the text to remove all punctuation before counting words
    raw_text = ' '.join([entry[0] for entry in entries])
    clean_text = re.sub(r'[^\w\s]', '', raw_text).lower()
    
    words = [word for word in clean_text.split() if word not in STOP_WORDS]
    
    # --- START OF UPGRADE: Find both single words and two-word phrases ---

    # 1. Count single words (unigrams)
    word_counts = Counter(words)
    top_single_words = [word for word, count in word_counts.most_common(10)]

    # 2. Count two-word phrases (bigrams)
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    bigram_counts = Counter(bigrams)
    top_phrases = [phrase for phrase, count in bigram_counts.most_common(10)]

    # 3. Combine them into one list of topics, removing duplicates
    all_top_topics = list(dict.fromkeys(top_phrases + top_single_words))

    # --- END OF UPGRADE ---

    insights = []
    
    for topic in all_top_topics:
        # We search for the topic string in the original, lowercased text
        related_entries = [entry for entry in entries if topic in entry[0].lower()]
        
        mention_count = len(related_entries)
        
        # We still require at least 2 mentions for a reliable insight
        if mention_count < 2:
            continue

        mood_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        avg_mood = sum(mood_map.get(entry[1], 0) for entry in related_entries) / mention_count
        avg_prod = sum(entry[2] for entry in related_entries) / mention_count

        insight_data = {
            'topic': topic,
            'count': mention_count,
            'avg_mood': avg_mood,
            'avg_prod': avg_prod
        }
        insights.append(insight_data)

    return insights

