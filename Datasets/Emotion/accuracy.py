import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import time

# Load data
df = pd.read_csv('Datasets/Emotion/test_converted.csv')

texts = df['text'].tolist()
labels = df['mood'].tolist()

# Split into train and test (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train logistic regression classifier
clf = LogisticRegression(max_iter=1000)
start_time = time.time()
clf.fit(X_train_tfidf, y_train)
end_time = time.time()
training_time = end_time - start_time

# Predict on test data
start_time = time.time()
y_pred = clf.predict(X_test_tfidf)
end_time = time.time()
inference_time = end_time - start_time

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Training time: {training_time:.4f} seconds")
print(f"Inference time on {len(X_test)} samples: {inference_time:.4f} seconds")
print(f"Accuracy: {accuracy:.4f}\n")

print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
