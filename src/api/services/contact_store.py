"""Simple SQLite-backed contact message store for local development.

This module ensures a `contacts.db` SQLite file exists under `data/` and
provides functions to insert and list messages.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "contacts.sqlite"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id TEXT PRIMARY KEY,
            full_name TEXT,
            organization TEXT,
            email TEXT,
            phone TEXT,
            subject TEXT,
            message TEXT,
            received_at TEXT,
            status TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_message(entry: Dict[str, Any]) -> None:
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO contact_messages (id, full_name, organization, email, phone, subject, message, received_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry["id"],
            entry.get("full_name"),
            entry.get("organization"),
            entry.get("email"),
            entry.get("phone"),
            entry.get("subject"),
            entry.get("message"),
            entry.get("received_at"),
            entry.get("status", "queued"),
        ),
    )
    conn.commit()
    conn.close()


def list_messages(limit: int = 100) -> list[Dict[str, Any]]:
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contact_messages ORDER BY received_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
