import sqlite3
from datetime import datetime

DB_NAME = "quiz_history.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            difficulty TEXT,
            score INTEGER,
            total INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_history(topic, difficulty, score, total):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO quiz_history (topic, difficulty, score, total, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (topic, difficulty, score, total, datetime.now()))
    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT topic, difficulty, score, total, timestamp FROM quiz_history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows
