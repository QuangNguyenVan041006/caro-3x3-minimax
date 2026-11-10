"""Tài khoản và lịch sử được lưu trên máy bằng SQLite."""
import hashlib
import hmac
import re
import secrets
import sqlite3
from pathlib import Path

class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY COLLATE NOCASE, salt BLOB NOT NULL,
            password BLOB NOT NULL, language TEXT NOT NULL DEFAULT 'vi');
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY, username TEXT NOT NULL, mode TEXT NOT NULL,
            human TEXT NOT NULL, outcome TEXT NOT NULL,
            played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        ''')

    @staticmethod
    def digest(password, salt):
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 600000)

    def register(self, name, password):
        name = name.strip()
        if not re.fullmatch(r'[A-Za-z0-9_]{3,24}', name):
            return 'invalid_name'
        if len(password) < 6:
            return 'short_password'
        salt = secrets.token_bytes(16)
        try:
            with self.db:
                self.db.execute('INSERT INTO users(name,salt,password) VALUES(?,?,?)',
                                (name, salt, self.digest(password, salt)))
        except sqlite3.IntegrityError:
            return 'exists'
        return None

    def login(self, name, password):
        row = self.db.execute('SELECT name,salt,password,language FROM users WHERE name=?',
                              (name.strip(),)).fetchone()
        if row and hmac.compare_digest(row[2], self.digest(password, row[1])):
            return row[0], row[3]
        return None

    def language(self, name, lang):
        with self.db:
            self.db.execute('UPDATE users SET language=? WHERE name=?', (lang, name))

    def record(self, name, mode, human, outcome):
        with self.db:
            self.db.execute('INSERT INTO games(username,mode,human,outcome) VALUES(?,?,?,?)',
                            (name, mode, human, outcome))

    def history(self, name):
        return self.db.execute('SELECT played_at,mode,human,outcome FROM games '
                               'WHERE username=? ORDER BY id DESC LIMIT 100', (name,)).fetchall()

    def close(self):
        self.db.close()
