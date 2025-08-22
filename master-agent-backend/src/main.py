from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Master Agent Backend API',
        'status': 'running',
        'version': 'new-1.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/test')
def test():
    return jsonify({'message': 'New backend API is working'})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    return jsonify({'response': f'You said: {message}'})

# ❌ No app.run() needed for App Engine, Gunicorn will start it