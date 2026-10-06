"""Tiny SQLite key-value store scoped per chat."""
import json
import sqlite3
from pathlib import Path

_db = sqlite3.connect(Path(__file__).with_name("bot.db"), check_same_thread=False)
_db.execute(
    "CREATE TABLE IF NOT EXISTS kv (chat_id INTEGER, key TEXT, value TEXT, "
    "PRIMARY KEY (chat_id, key))"
)


def get(chat_id, key, default=None):
    row = _db.execute(
        "SELECT value FROM kv WHERE chat_id=? AND key=?", (chat_id, key)
    ).fetchone()
    return json.loads(row[0]) if row else default


def put(chat_id, key, value):
    _db.execute(
        "INSERT OR REPLACE INTO kv VALUES (?,?,?)", (chat_id, key, json.dumps(value))
    )
    _db.commit()


def delete(chat_id, key):
    _db.execute("DELETE FROM kv WHERE chat_id=? AND key=?", (chat_id, key))
    _db.commit()
