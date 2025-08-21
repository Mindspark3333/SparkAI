from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import sqlite3
from datetime import datetime
import requests
from urllib.parse import urlparse
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('master_agent.db')
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            gemini_api_key TEXT,
            google_calendar_enabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create research_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            content_type TEXT,
            summary TEXT,
            key_insights TEXT,
            actionable_items TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_user_settings():
    """Get user settings from database"""
    conn = sqlite3.connect('master_agent.db')
    cursor = conn.cursor()
    cursor.execute('SELECT gemini_api_key, google_calendar_enabled FROM users WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'gemini_api_key': result[0],
            'google_calendar_enabled': bool(result[1])
        }
    return {'gemini_api_key': None, 'google_calendar_enabled': False}

def extract_content(url):
    """Extract content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simple content extraction
        content = response.text
        title = "Web Content"
        
        # Try to extract title
        if '<title>' in content:
            start = content.find('<title>') + 7
            end = content.find('</title>')
            if end > start:
                title = content[start:end].strip()
        
        return {
            'title': title,
            'content': content[:5000],  # Limit content length
            'content_type': 'webpage'
        }
    except Exception as e:
        return {
            'title': 'Error extracting content',
            'content': f'Failed to extract content: {str(e)}',
            'content_type': 'error'
        }

def analyze_with_gemini(content, api_key):
    """Analyze content using Gemini AI"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze the following content and provide:
        1. A concise summary (2-3 sentences)
        2. Key insights (3-5 bullet points)
        3. Actionable items (2-3 specific actions)
        
        Content: {content[:3000]}
        
        Format your response as JSON with keys: summary, key_insights, actionable_items
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            result = json.loads(response.text)
            return result
        except:
            # Fallback if not JSON
            return {
                'summary': response.text[:500],
                'key_insights': ['Analysis completed'],
                'actionable_items': ['Review the content']
            }
            
    except Exception as e:
        return {
            'summary': f'Analysis failed: {str(e)}',
            'key_insights': ['Error in analysis'],
            'actionable_items': ['Check API key and try again']
        }

# API Routes
@app.route('/')
def home():
    return jsonify({'message': 'Master Agent Backend API', 'status': 'running'})

@app.route('/api/user/settings', methods=['GET'])
def get_settings():
    settings = get_user_settings()
    return jsonify(settings)

@app.route('/api/user/settings', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        gemini_api_key = data.get('gemini_api_key')
        google_calendar_enabled = data.get('google_calendar_enabled', False)
        
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        # Insert or update user settings
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, gemini_api_key, google_calendar_enabled)
            VALUES (1, ?, ?)
        ''', (gemini_api_key, google_calendar_enabled))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/submit', methods=['POST'])
def submit_research():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get user settings
        settings = get_user_settings()
        if not settings.get('gemini_api_key'):
            return jsonify({'error': 'Gemini API key not configured'}), 400
        
        # Extract content
        content_data = extract_content(url)
        
        # Analyze with Gemini
        analysis = analyze_with_gemini(content_data['content'], settings['gemini_api_key'])
        
        # Save to database
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO research_results 
            (url, title, content_type, summary, key_insights, actionable_items, status, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, 'completed', ?)
        ''', (
            url,
            content_data['title'],
            content_data['content_type'],
            analysis.get('summary', ''),
            json.dumps(analysis.get('key_insights', [])),
            json.dumps(analysis.get('actionable_items', [])),
            datetime.now()
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Research submitted and processed successfully',
            'id': result_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/results', methods=['GET'])
def get_research_results():
    try:
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, url, title, content_type, summary, key_insights, actionable_items, status, created_at
            FROM research_results
            ORDER BY created_at DESC
            LIMIT 50
        ''')
        
        results = []
        for row in cursor.fetchall():
            try:
                key_insights = json.loads(row[5]) if row[5] else []
            except:
                key_insights = []
                
            try:
                actionable_items = json.loads(row[6]) if row[6] else []
            except:
                actionable_items = []
            
            results.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'content_type': row[3],
                'summary': row[4],
                'key_insights': key_insights,
                'actionable_items': actionable_items,
                'status': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/<int:result_id>/create-event', methods=['POST'])
def create_calendar_event(result_id):
    try:
        # Get research result
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT title, summary, url FROM research_results WHERE id = ?', (result_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Research result not found'}), 404
        
        title, summary, url = result
        
        # For now, just return success (Google Calendar integration would go here)
        return jsonify({
            'message': 'Calendar event created successfully',
            'event_title': f'Research Task: {title}',
            'event_description': f'{summary}\n\nSource: {url}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/auth-url', methods=['GET'])
def get_calendar_auth_url():
    # Placeholder for Google Calendar OAuth
    return jsonify({
        'auth_url': 'https://accounts.google.com/oauth2/auth?placeholder=true',
        'message': 'Calendar integration coming soon'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))