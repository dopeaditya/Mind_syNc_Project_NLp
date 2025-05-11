
from flask import Flask, render_template, request, redirect
from nlp.analysis import analyze_text
from nlp.task_extractor import extract_tasks
from utils.scorer import productivity_score
import sqlite3
from datetime import datetime
import os
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["journal"]
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
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect('database/journal.db')
    c = conn.cursor()
    c.execute("SELECT date, mood, productivity FROM entries ORDER BY date DESC")
    entries = c.fetchall()
    c.execute("SELECT id, task_text FROM tasks WHERE status = 'pending'")
    pending_tasks = c.fetchall()
    conn.close()
    return render_template("dashboard.html", entries=entries, pending_tasks=pending_tasks)

@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    conn = sqlite3.connect('database/journal.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
