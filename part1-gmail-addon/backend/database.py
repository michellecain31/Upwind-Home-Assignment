# כל סריקה שנעשית נשמרת פה - זה מה שמאפשר לנו להציג היסטוריה

import sqlite3
import json
from datetime import datetime

DB_PATH = "scans.db"


# יוצרת את הטבלה אם היא עדיין לא קיימת - רצה פעם אחת בעליית השרת
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            verdict TEXT,
            total_score INTEGER,
            signals TEXT,
            scanned_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# שומרת סריקה חדשה - הsignals הם רשימה אז הופכים אותם ל-JSON לפני השמירה
def save_scan(sender: str, subject: str, verdict: str, total_score: int, signals: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (sender, subject, verdict, total_score, signals, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sender, subject, verdict, total_score, json.dumps(signals), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


# מחזירה את הסריקות האחרונות, מהחדשה לישנה
def get_recent_scans(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, subject, verdict, total_score, signals, scanned_at
        FROM scans
        ORDER BY scanned_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "sender": r[0],
            "subject": r[1],
            "verdict": r[2],
            "total_score": r[3],
            "signals": json.loads(r[4]),
            "scanned_at": r[5]
        }
        for r in rows
    ]