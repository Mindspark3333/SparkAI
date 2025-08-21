from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sqlite3, json, requests, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Use /tmp for SQLite on App Engine
DB_PATH = os.getenv("DB_PATH", "/tmp/master_agent.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                gemini_api_key TEXT,
                google_calendar_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
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
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                           ('default_user', 'user@example.com'))
        conn.commit()
        conn.close()
        logger.info("DB ready at %s", DB_PATH)
    except Exception as e:
        logger.exception("DB init error")

@app.before_first_request
def _init():
    init_db()

class ContentExtractor:
    @staticmethod
    def extract_from_url(url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.text
            title = "Web Content"
            if '<title>' in content:
                start, end = content.find('<title>')+7, content.find('</title>')
                if end > start:
                    title = content[start:end].strip()
            return {'title': title, 'content': content[:5000], 'success': True}
        except Exception as e:
            return {'title': 'Error', 'content': f"Failed: {e}", 'success': False}

class GeminiAnalyzer:
    @staticmethod
    def analyze_content(content, title, gemini_api_key):
        try:
            if not gemini_api_key:
                return {'summary': 'No API key', 'key_insights': 'Need key', 'analysis': 'Missing key'}
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
            prompt = f"""Analyze content:
            Title: {title}
            Content: {content[:3000]}"""
            payload = {"contents":[{"parts":[{"text":prompt}]}]}
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            result = r.json()
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text']
                try:
                    return json.loads(text)
                except:
                    return {'summary': text[:200], 'key_insights': 'ok', 'analysis': text}
            return {'summary': 'done', 'key_insights': 'ok', 'analysis': 'done'}
        except Exception as e:
            return {'summary': f'Error: {e}', 'key_insights': 'fail', 'analysis': 'check key'}

@app.route('/')
def home():
    return jsonify({'message':'Master Agent Backend','status':'running'})

@app.route('/api/research/submit', methods=['POST'])
def submit_research():
    try:
        data = request.get_json()
        url = data.get('url')
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, gemini_api_key FROM users WHERE username=?", ('default_user',))
        user = c.fetchone()
        if not user: return jsonify({'error':'user not found'}),404
        uid, key = user
        ext = ContentExtractor.extract_from_url(url)
        ana = GeminiAnalyzer.analyze_content(ext['content'], ext['title'], key)
        c.execute('''INSERT INTO research_results
                     (user_id,url,title,content,summary,key_insights,analysis,status)
                     VALUES (?,?,?,?,?,?,?,?)''',
                     (uid,url,ext['title'],ext['content'],
                      ana['summary'],ana['key_insights'],ana['analysis'],'completed'))
        rid = c.lastrowid
        conn.commit(); conn.close()
        return jsonify({'id':rid,'title':ext['title'],'summary':ana['summary'],'status':'completed'})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/api/research/results')
def get_research_results():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id,url,title,summary,key_insights,analysis,status,created_at FROM research_results ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall(); conn.close()
    return jsonify([{'id':r[0],'url':r[1],'title':r[2],'summary':r[3],'key_insights':r[4],'analysis':r[5],'status':r[6],'created_at':r[7]} for r in rows])

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    d = request.get_json(); key = d.get('gemini_api_key')
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE users SET gemini_api_key=? WHERE username=?", (key,'default_user'))
    conn.commit(); conn.close()
    return jsonify({'message':'saved'})

@app.route('/api/settings')
def get_settings():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT gemini_api_key FROM users WHERE username=?", ('default_user',))
    r = c.fetchone(); conn.close()
    return jsonify({'gemini_api_key': r[0] if r else '', 'google_calendar_connected': False})

@app.route('/api/calendar/events')
def get_calendar_events(): return jsonify([])

@app.route('/api/calendar/create', methods=['POST'])
def create_calendar_event(): return jsonify({'message':'created','id':'placeholder'})

# no app.run() -> Gunicorn handles it