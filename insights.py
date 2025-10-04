import sqlite3
import re
from collections import defaultdict
import math # We need the math library for the IDF calculation

# The STOP_WORDS list is still useful for removing the absolute most common words.
STOP_WORDS = [
    'a', 'about', 'am', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 
    'being', 'but', 'by', 'can', 'did', 'do', 'does', 'doing', 'don', 
    'for', 'from', 'had', 'has', 'have', 'having', 'he', 'her', 'him', 
    'his', 'i', 'if', 'in', 'is', 'it', 'its', 'just', 'me', 'my', 'myself', 
    'now', 'of', 'off', 'on', 'or', 'our', 'ours', 's', 'she', 'should', 
    'so', 't', 'that', 'the', 'their', 'them', 'then', 'these', 'they', 
    'this', 'those', 'to', 'too', 'was', 'we', 'were', 'what', 'which', 
    'who', 'whom', 'will', 'with', 'you', 'your', 'yours'
]

def generate_insights(period="all"):
    """
    Analyzes entries using the TF-IDF algorithm to find the most important topics.
    """
    conn = sqlite3.connect('database/journal.db')
    cursor = conn.cursor()

    if period == "weekly":
        query = "SELECT text, mood, productivity FROM entries WHERE date >= date('now', '-7 days')"
    elif period == "monthly":
        query = "SELECT text, mood, productivity FROM entries WHERE date >= date('now', '-30 days')"
    else:
        query = "SELECT text, mood, productivity FROM entries"
        
    cursor.execute(query)
    entries = cursor.fetchall()
    conn.close()

    if len(entries) < 2: # TF-IDF needs at least 2 documents to work well
        return []

    # --- START of New TF-IDF Logic ---

    # 1. Pre-process all documents
    processed_docs = []
    for entry in entries:
        raw_text = entry[0]
        clean_text = re.sub(r'[^\w\s]', '', raw_text).lower()
        words = [word for word in clean_text.split() if word not in STOP_WORDS]
        processed_docs.append(words)

    # 2. Calculate Term Frequency (TF) for each document
    tf_scores = []
    for doc in processed_docs:
        doc_tf = defaultdict(int)
        for word in doc:
            doc_tf[word] += 1
        # Normalize by dividing by the total number of words in the document
        for word, count in doc_tf.items():
            doc_tf[word] = count / len(doc)
        tf_scores.append(doc_tf)

    # 3. Calculate Inverse Document Frequency (IDF) for all words
    doc_count = len(entries)
    word_doc_counts = defaultdict(int)
    all_words = set(word for doc in processed_docs for word in doc)
    
    for word in all_words:
        for doc in processed_docs:
            if word in doc:
                word_doc_counts[word] += 1

    idf_scores = {}
    for word, count in word_doc_counts.items():
        idf_scores[word] = math.log(doc_count / (1 + count)) # Use log to smooth the scores

    # 4. Calculate TF-IDF scores and find the most important words
    tfidf_scores = defaultdict(float)
    for i, doc in enumerate(processed_docs):
        for word in doc:
            tfidf_scores[word] += tf_scores[i][word] * idf_scores[word]
            
    # Get the top 10 words with the highest total TF-IDF scores
    top_topics = sorted(tfidf_scores.items(), key=lambda item: item[1], reverse=True)[:10]
    top_topics = [word for word, score in top_topics]

    # --- END of New TF-IDF Logic ---

    insights = []
    
    for topic in top_topics:
        related_entries = [entry for entry in entries if topic in entry[0].lower()]
        mention_count = len(related_entries)
        
        if mention_count < 2 and len(top_topics) > 1: # Be a bit more lenient if only one topic found
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

