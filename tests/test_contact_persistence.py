import requests
import sqlite3
from pathlib import Path
import time


def test_contact_persistence():
    url = "http://127.0.0.1:8000/api/v1/contact/messages"
    payload = {
        "full_name": "Persistence Test",
        "organization": "Test Org",
        "email": "persist@example.com",
        "phone": "+000",
        "subject": "Persistence",
        "message": "Persist test message",
    }
    resp = requests.post(url, json=payload, timeout=10)
    assert resp.status_code in (200, 201)
    data = resp.json()
    request_id = data.get("request_id")
    assert request_id

    # check sqlite file
    db_path = Path("src") / "data" / "contacts.sqlite"
    # allow small delay for write
    time.sleep(0.2)
    assert db_path.exists(), "contacts.sqlite not found"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT id, full_name FROM contact_messages WHERE id = ?", (request_id,))
    row = cur.fetchone()
    conn.close()
    assert row is not None and row[1] == "Persistence Test"
