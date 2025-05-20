# Define the emotion mapping
emotion_to_mood = {
    "joy": "positive",
    "love": "positive",
    "happy": "positive",

    "anger": "negative",
    "sadness": "negative",
    "fear": "negative",
    "disgust": "negative",
    "hate": "negative",
    "shame": "negative",
    "guilt": "negative",

    "surprise": "neutral",
    "neutral": "neutral",
    "boredom": "neutral",
    "calm": "neutral"
}

# Read and convert the dataset
input_file = "train.txt"  # Your original dataset
output_file = "converted_dataset.csv"   # Output file

with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
    fout.write("text,mood\n")  # CSV header

    for line in fin:
        line = line.strip()
        if not line or ";" not in line:
            continue
        
        text, emotion = line.rsplit(";", 1)
        mood = emotion_to_mood.get(emotion.strip().lower())

        if mood:  # Only include if mapping exists
            # Escape commas in text to not break CSV
            safe_text = text.replace('"', '""')
            fout.write(f'"{safe_text}",{mood}\n')
