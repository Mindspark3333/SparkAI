from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
import json
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('master_agent.db')
    cursor = conn.cursor()
    
    # Create users table
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
    
    # Create research_results table
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
    
    # Create default user if not exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, email) 
            VALUES ('default_user', 'user@example.com')
        ''')
    
    conn.commit()
    conn.close()

# Content extraction service
class ContentExtractor:
    @staticmethod
    def extract_from_url(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Simple text extraction (you can enhance this with BeautifulSoup)
            content = response.text
            title = "Web Content"
            
            # Extract title if HTML
            if '<title>' in content:
                start = content.find('<title>') + 7
                end = content.find('</title>')
                if end > start:
                    title = content[start:end].strip()
            
            return {
                'title': title,
                'content': content[:5000],  # Limit content length
                'success': True
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return {
                'title': 'Error',
                'content': f"Failed to extract content: {str(e)}",
                'success': False
            }

# Gemini AI analyzer
class GeminiAnalyzer:
    @staticmethod
    def analyze_content(content, title, gemini_api_key):
        try:
            if not gemini_api_key:
                return {
                    'summary': 'No API key provided',
                    'key_insights': 'Please configure your Gemini API key',
                    'analysis': 'API key required for analysis'
                }
            
            # Gemini API call
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
            
            prompt = f"""
            Analyze the following content and provide:
            1. A concise summary (2-3 sentences)
            2. Key insights (3-5 bullet points)
            3. Detailed analysis (1-2 paragraphs)
            
            Title: {title}
            Content: {content[:3000]}
            
            Format your response as JSON with keys: summary, key_insights, analysis
            """
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Try to parse as JSON, fallback to simple parsing
                try:
                    parsed = json.loads(text)
                    return parsed
                except:
                    return {
                        'summary': text[:200] + '...' if len(text) > 200 else text,
                        'key_insights': 'Analysis completed successfully',
                        'analysis': text
                    }
            else:
                return {
                    'summary': 'Analysis completed',
                    'key_insights': 'Content processed successfully',
                    'analysis': 'Gemini analysis completed'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing content with Gemini: {str(e)}")
            return {
                'summary': f'Analysis error: {str(e)}',
                'key_insights': 'Failed to analyze content',
                'analysis': 'Please check your API key and try again'
            }

# Routes
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Master Agent Backend API',
        'version': '2.0',
        'status': 'running'
    })

@app.route('/api/research/submit', methods=['POST'])
def submit_research():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get user (default user for now)
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, gemini_api_key FROM users WHERE username = ?', ('default_user',))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_id, gemini_api_key = user
        
        # Extract content
        extraction_result = ContentExtractor.extract_from_url(url)
        
        # Analyze with Gemini
        analysis_result = GeminiAnalyzer.analyze_content(
            extraction_result['content'],
            extraction_result['title'],
            gemini_api_key
        )
        
        # Save to database
        cursor.execute('''
            INSERT INTO research_results 
            (user_id, url, title, content, summary, key_insights, analysis, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            url,
            extraction_result['title'],
            extraction_result['content'],
            analysis_result['summary'],
            analysis_result['key_insights'],
            analysis_result['analysis'],
            'completed'
        ))
        
        research_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': research_id,
            'message': 'Research submitted successfully',
            'status': 'completed',
            'title': extraction_result['title'],
            'summary': analysis_result['summary']
        })
        
    except Exception as e:
        logger.error(f"Error submitting research: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/results', methods=['GET'])
def get_research_results():
    try:
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, url, title, summary, key_insights, analysis, status, created_at
            FROM research_results
            ORDER BY created_at DESC
            LIMIT 50
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'summary': row[3],
                'key_insights': row[4],
                'analysis': row[5],
                'status': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error getting research results: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        gemini_api_key = data.get('gemini_api_key')
        
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET gemini_api_key = ? WHERE username = ?
        ''', (gemini_api_key, 'default_user'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Settings saved successfully'})
        
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        conn = sqlite3.connect('master_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT gemini_api_key FROM users WHERE username = ?', ('default_user',))
        result = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'gemini_api_key': result[0] if result and result[0] else '',
            'google_calendar_connected': False
        })
        
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    # Placeholder for calendar integration
    return jsonify([])

@app.route('/api/calendar/create', methods=['POST'])
def create_calendar_event():
    # Placeholder for calendar event creation
    data = request.get_json()
    return jsonify({'message': 'Calendar event created', 'id': 'placeholder'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
