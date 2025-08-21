from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# In-memory settings storage (no database)
settings_store = {
    'gemini_api_key': ''
}

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
    return jsonify({
        'gemini_api_key': settings_store.get('gemini_api_key', '')
    })

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        gemini_api_key = data.get('gemini_api_key', '')
        
        # Store in memory
        settings_store['gemini_api_key'] = gemini_api_key
        
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    return jsonify({'response': f'You said: {message}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)