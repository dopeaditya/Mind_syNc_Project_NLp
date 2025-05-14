from flask import Flask, render_template, request, redirect, jsonify
from nlp.analysis import analyze_text
from nlp.task_extractor import extract_tasks
from utils.scorer import productivity_score
import sqlite3
from datetime import datetime
import os
from collections import defaultdict

app = Flask(__name__)

def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')

    conn = sqlite3.connect('database/journal.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            text TEXT,
            mood TEXT,
            productivity REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER,
            task_text TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    conn = sqlite3.connect('database/journal.db')
    c = conn.cursor()

    # Fetch journal entries
    c.execute("SELECT date, text, mood, productivity FROM entries ORDER BY date ASC")
    raw_entries = c.fetchall()

    # Fetch only pending and not completed tasks
    c.execute("SELECT id, task_text FROM tasks WHERE status = 'pending' AND completed = 0")
    pending_tasks = c.fetchall()

    conn.close()

    # Group entries by date
    grouped = defaultdict(list)
    for entry in raw_entries:
        grouped[entry[0]].append(entry)

    entries_by_day = []
    mood_score_map = {"negative": -1, "neutral": 0, "positive": 1}

    for date, items in grouped.items():
        moods = [e[2] for e in items]
        prod_scores = [e[3] for e in items]
        mood_numeric = [mood_score_map.get(m, 0) for m in moods]

        avg_mood_score = sum(mood_numeric) / len(mood_numeric)
        avg_prod_score = sum(prod_scores) / len(prod_scores)

        # Sort entries oldest to newest and enumerate
        numbered_entries = list(enumerate(items, start=1))

        entries_by_day.append({
            "date": date,
            "avg_mood_score": round(avg_mood_score, 2),
            "avg_productivity": round(avg_prod_score, 2),
            "entries": numbered_entries
        })

    # Sort by date (latest last)
    entries_by_day.sort(key=lambda x: x["date"])

    return render_template("index.html", entries_by_day=entries_by_day, pending_tasks=pending_tasks)

@app.route("/submit_journal_ajax", methods=["POST"])
def submit_journal_ajax():
    data = request.get_json()
    text = data["journal"]
    analysis = analyze_text(text)
    prod_score = productivity_score(text)

    conn = sqlite3.connect('database/journal.db')
    c = conn.cursor()
    c.execute("INSERT INTO entries (date, text, mood, productivity) VALUES (?, ?, ?, ?)",
              (datetime.now().date(), text, analysis['mood'], prod_score))
    entry_id = c.lastrowid

    tasks = extract_tasks(text)
    for task in tasks:
        c.execute("INSERT INTO tasks (entry_id, task_text) VALUES (?, ?)", (entry_id, task))
    conn.commit()
    conn.close()

    return jsonify({
        "mood": analysis['mood'],
        "productivity": prod_score,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "tasks": tasks
    })

# @app.route("/dashboard")
# def dashboard():
#     conn = sqlite3.connect('database/journal.db')
#     c = conn.cursor()
#     c.execute("SELECT date, mood, productivity FROM entries ORDER BY date DESC")
#     entries = c.fetchall()
#     c.execute("SELECT id, task_text FROM tasks WHERE status = 'pending'")
#     pending_tasks = c.fetchall()
#     conn.close()
#     return render_template("dashboard.html", entries=entries, pending_tasks=pending_tasks)

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    conn = sqlite3.connect('database/journal.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return '', 204  # ✅ No Content — good for AJAX requests

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
