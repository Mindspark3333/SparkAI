from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sqlite3
import json
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('master_agent.db')
    cursor = conn.cursor()
    
    # Users table for settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            gemini_api_key TEXT,
            google_calendar_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Research results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            title TEXT,
            content TEXT,
            summary TEXT,
            key_insights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Calendar events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default user if not exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username) VALUES (?)', ('default_user',))
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return jsonify({
        'message': 'Master Agent Backend API',
        'status': 'running',
        'version': '2.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Settings endpoints
@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('SELECT gemini_api_key, google_calendar_token FROM users WHERE username = ?', ('default_user',))
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'gemini_api_key': result[0] if result and result[0] else '',
            'google_calendar_connected': bool(result and result[1])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        gemini_api_key = data.get('gemini_api_key', '')
        
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET gemini_api_key = ? WHERE username = ?', 
                      (gemini_api_key, 'default_user'))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Research endpoints
@app.route('/api/research/submit', methods=['POST'])
def submit_research():
    try:
        data = request.get_json()
        url = data.get('url', '')
        text_content = data.get('text', '')
        
        if not url and not text_content:
            return jsonify({'error': 'URL or text content required'}), 400
        
        # Get user's Gemini API key
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, gemini_api_key FROM users WHERE username = ?', ('default_user',))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        user_id, gemini_api_key = user
        
        # Extract content from URL if provided
        content = text_content
        title = 'Text Analysis'
        
        if url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                content = response.text[:5000]  # Limit content
                title = f'Analysis of {url}'
            except:
                content = f'Could not fetch content from {url}'
        
        # Analyze with Gemini if API key is available
        summary = 'Content submitted for analysis'
        insights = 'Analysis pending'
        
        if gemini_api_key:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
                prompt = f"Analyze this content and provide a summary and key insights:\n\n{content[:3000]}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                gemini_response = requests.post(gemini_url, json=payload, timeout=30)
                if gemini_response.status_code == 200:
                    result = gemini_response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        analysis = result['candidates'][0]['content']['parts'][0]['text']
                        summary = analysis[:500] + '...' if len(analysis) > 500 else analysis
                        insights = analysis
            except:
                pass  # Use default values if Gemini fails
        
        # Save to database
        cursor.execute('''
            INSERT INTO research_results (user_id, url, title, content, summary, key_insights)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, url, title, content, summary, insights))
        
        research_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': research_id,
            'message': 'Research submitted successfully',
            'title': title,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/results', methods=['GET'])
def get_research_results():
    try:
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, url, title, summary, key_insights, created_at
            FROM research_results
            ORDER BY created_at DESC
            LIMIT 20
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'summary': row[3],
                'key_insights': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Calendar endpoints
@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    try:
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, description, start_time, end_time, created_at
            FROM calendar_events
            ORDER BY start_time ASC
            LIMIT 50
        ''')
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'start_time': row[3],
                'end_time': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return jsonify(events)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/create', methods=['POST'])
def create_calendar_event():
    try:
        data = request.get_json()
        title = data.get('title', '')
        description = data.get('description', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', ('default_user',))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        cursor.execute('''
            INSERT INTO calendar_events (user_id, title, description, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user[0], title, description, start_time, end_time))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': event_id,
            'message': 'Calendar event created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Chat endpoint (existing)
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({'response': f'You said: {message}'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)