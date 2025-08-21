from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)
CORS(app)

# Simple database initialization
def init_db():
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                gemini_api_key TEXT
            )
        ''')
        # Insert default row if not exists
        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO settings (id, gemini_api_key) VALUES (1, "")')
        conn.commit()
        conn.close()
    except:
        pass  # Ignore database errors for now

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

@app.route('/api/test')
def test():
    return jsonify({'message': 'API is working'})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT gemini_api_key FROM settings WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'gemini_api_key': result[0] if result else ''
        })
    except:
        return jsonify({'gemini_api_key': ''})

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        gemini_api_key = data.get('gemini_api_key', '')
        
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE settings SET gemini_api_key = ? WHERE id = 1', (gemini_api_key,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({'response': f'You said: {message}'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)