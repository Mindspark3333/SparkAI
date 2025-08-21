from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sqlite3, json, requests, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# --- SQLite path (App Engine allows writes only in /tmp) ---
DB_PATH = "/tmp/master_agent.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            gemini_api_key TEXT,
            google_calendar_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT NOT NULL,
            title TEXT,
            content TEXT,
            summary TEXT,
            key_insights TEXT,
            analysis TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                  ("default_user", "user@example.com"))
    conn.commit(); conn.close()
    logger.info("DB initialized at %s", DB_PATH)

@app.before_first_request
def _init():
    init_db()

# --- Routes ---
@app.route('/')
def home():
    return jsonify({"message": "Master Agent Backend API", "status": "running"})

@app.route('/api/settings')
def get_settings():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT gemini_api_key FROM users WHERE username=?", ("default_user",))
    r = c.fetchone(); conn.close()
    return jsonify({"gemini_api_key": r[0] if r else "", "google_calendar_connected": False})

@app.route('/api/settings/save', methods=["POST"])
def save_settings():
    d = request.get_json()
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE users SET gemini_api_key=? WHERE username=?", (d.get("gemini_api_key"), "default_user"))
    conn.commit(); conn.close()
    return jsonify({"message": "saved"})

# (keep your other routes if needed… simplified here)

# ❌ DO NOT add `if __name__ == "__main__": app.run()`
# Gunicorn handles startup