"""YouTube Data API の取得結果を SQLite に一時保存するキャッシュ。

同じチャンネルを何度分析されても API を叩かないようにしてクォータを節約する。
YouTube API の規約に合わせ、保存期間は最大でも30日未満にすること。
"""
import json
import os
import sqlite3
import time

DB_PATH = os.getenv('CACHE_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache.sqlite3'))
DEFAULT_TTL = int(os.getenv('CACHE_TTL_SECONDS', str(12 * 60 * 60)))  # 既定は12時間


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL, expires_at REAL NOT NULL)')
    return conn


def get(key):
    with _connect() as conn:
        row = conn.execute('SELECT value, expires_at FROM cache WHERE key = ?', (key,)).fetchone()
        if row is None:
            return None
        if row[1] < time.time():
            conn.execute('DELETE FROM cache WHERE key = ?', (key,))
            return None
        return json.loads(row[0])


def set(key, value, ttl=DEFAULT_TTL):
    with _connect() as conn:
        conn.execute('REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)',
                     (key, json.dumps(value, ensure_ascii=False), time.time() + ttl))
        conn.execute('DELETE FROM cache WHERE expires_at < ?', (time.time(),))
