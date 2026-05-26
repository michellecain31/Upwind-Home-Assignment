# Database abstraction layer for persistent storage and historical audit tracking.

import json
import sqlite3
from datetime import datetime

DB_PATH = "scans.db"


def init_db():
    """Initializes schema on application startup if database table is absent."""
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


def save_scan(
    sender: str, subject: str, verdict: str, total_score: int, signals: list
):
    """Persists evaluation context, serializing complex objects into JSON text."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scans (sender, subject, verdict, total_score, signals, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            sender,
            subject,
            verdict,
            total_score,
            json.dumps(signals),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_recent_scans(limit: int = 20):
    """Retrieves recent evaluation logs sorted by chronological recency."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT sender, subject, verdict, total_score, signals, scanned_at
        FROM scans
        ORDER BY scanned_at DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "sender": r[0],
            "subject": r[1],
            "verdict": r[2],
            "total_score": r[3],
            "signals": json.loads(r[4]),  # Deserializes telemetry breakdown
            "scanned_at": r[5],
        }
        for r in rows
    ]