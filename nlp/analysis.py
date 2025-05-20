from textblob import TextBlob
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer

def analyze_text(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    sia = SentimentIntensityAnalyzer()
    vader_score = sia.polarity_scores(text)

    mood = 'positive' if polarity > 0.2 else 'negative' if polarity < -0.2 else 'neutral'
    return {'polarity': polarity, 'vader': vader_score, 'mood': mood}
