from flask import Blueprint, jsonify, request, current_app
from src.models.master_agent import User, Task, Goal, Note, Conversation, db
from datetime import datetime
import os
import json
import uuid

master_agent_bp = Blueprint('master_agent', __name__)

# Chat endpoint
@master_agent_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 1)  # Default user for now
        message = data.get('message', '')
        
        # Simple response logic (can be enhanced with LLM integration)
        response = generate_response(message)
        
        # Save conversation
        conversation = Conversation(
            message=message,
            response=response,
            user_id=user_id
        )
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'response': response,
            'conversation_id': conversation.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_response(message):
    """Simple response generator - can be enhanced with LLM integration"""
    message_lower = message.lower()
    
    if 'task' in message_lower and ('create' in message_lower or 'add' in message_lower):
        return "I can help you create a task. Please use the task management interface or tell me more details about the task."
    elif 'goal' in message_lower:
        return "I can help you with goal tracking. What goal would you like to work on?"
    elif 'note' in message_lower:
        return "I can help you take notes. Would you like to create a text note or voice note?"
    elif 'hello' in message_lower or 'hi' in message_lower:
        return "Hello! I'm your Master Agent. I can help you manage tasks, track goals, take notes, and organize your life. How can I assist you today?"
    else:
        return "I understand you're asking about: " + message + ". How can I help you with this?"

# Task management endpoints
@master_agent_bp.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        tasks = Task.query.filter_by(user_id=user_id).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            user_id=data.get('user_id', 1)
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.json
        
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)
        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data['due_date'])
        
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Goal management endpoints
@master_agent_bp.route('/goals', methods=['GET'])
def get_goals():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        goals = Goal.query.filter_by(user_id=user_id).all()
        return jsonify([goal.to_dict() for goal in goals])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/goals', methods=['POST'])
def create_goal():
    try:
        data = request.json
        goal = Goal(
            title=data['title'],
            description=data.get('description', ''),
            target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None,
            progress=data.get('progress', 0),
            status=data.get('status', 'active'),
            user_id=data.get('user_id', 1)
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify(goal.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    try:
        goal = Goal.query.get_or_404(goal_id)
        data = request.json
        
        goal.title = data.get('title', goal.title)
        goal.description = data.get('description', goal.description)
        goal.progress = data.get('progress', goal.progress)
        goal.status = data.get('status', goal.status)
        if data.get('target_date'):
            goal.target_date = datetime.fromisoformat(data['target_date'])
        
        db.session.commit()
        return jsonify(goal.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    try:
        goal = Goal.query.get_or_404(goal_id)
        db.session.delete(goal)
        db.session.commit()
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Note management endpoints
@master_agent_bp.route('/notes', methods=['GET'])
def get_notes():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        notes = Note.query.filter_by(user_id=user_id).all()
        return jsonify([note.to_dict() for note in notes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/notes', methods=['POST'])
def create_note():
    try:
        data = request.json
        note = Note(
            title=data.get('title', ''),
            content=data.get('content', ''),
            note_type=data.get('note_type', 'text'),
            transcription=data.get('transcription', ''),
            user_id=data.get('user_id', 1)
        )
        
        if data.get('tags'):
            note.set_tags(data['tags'])
        
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        data = request.json
        
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.transcription = data.get('transcription', note.transcription)
        
        if data.get('tags'):
            note.set_tags(data['tags'])
        
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@master_agent_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        
        # Delete audio file if it exists
        if note.audio_file_path and os.path.exists(note.audio_file_path):
            os.remove(note.audio_file_path)
        
        db.session.delete(note)
        db.session.commit()
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Voice note upload endpoint
@master_agent_bp.route('/notes/voice', methods=['POST'])
def upload_voice_note():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        user_id = request.form.get('user_id', 1, type=int)
        title = request.form.get('title', '')
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'uploads', 'voice_notes')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.wav"
        file_path = os.path.join(upload_dir, filename)
        
        # Save audio file
        audio_file.save(file_path)
        
        # Import speech processing utilities
        try:
            from src.utils.speech_processing import transcribe_audio, validate_audio_file
            
            # Validate audio file
            is_valid, validation_message = validate_audio_file(file_path)
            if not is_valid:
                os.remove(file_path)  # Clean up invalid file
                return jsonify({'error': f'Invalid audio file: {validation_message}'}), 400
            
            # Transcribe audio to text
            transcription = transcribe_audio(file_path)
            
        except ImportError:
            transcription = "Transcription not available - speech processing dependencies not installed"
        except Exception as e:
            transcription = f"Transcription failed: {str(e)}"
        
        # Create note record
        note = Note(
            title=title or f"Voice Note {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            note_type='voice',
            audio_file_path=file_path,
            transcription=transcription,
            user_id=user_id
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify(note.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Conversation history endpoint
@master_agent_bp.route('/conversations', methods=['GET'])
def get_conversations():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        conversations = Conversation.query.filter_by(user_id=user_id)\
                                        .order_by(Conversation.created_at.desc())\
                                        .limit(limit).all()
        
        return jsonify([conv.to_dict() for conv in conversations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard stats endpoint
@master_agent_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Get task statistics
        total_tasks = Task.query.filter_by(user_id=user_id).count()
        completed_tasks = Task.query.filter_by(user_id=user_id, status='completed').count()
        pending_tasks = Task.query.filter_by(user_id=user_id, status='pending').count()
        
        # Get goal statistics
        total_goals = Goal.query.filter_by(user_id=user_id).count()
        active_goals = Goal.query.filter_by(user_id=user_id, status='active').count()
        completed_goals = Goal.query.filter_by(user_id=user_id, status='completed').count()
        
        # Get note statistics
        total_notes = Note.query.filter_by(user_id=user_id).count()
        text_notes = Note.query.filter_by(user_id=user_id, note_type='text').count()
        voice_notes = Note.query.filter_by(user_id=user_id, note_type='voice').count()
        
        # Get recent activity
        recent_tasks = Task.query.filter_by(user_id=user_id)\
                                .order_by(Task.created_at.desc())\
                                .limit(5).all()
        
        recent_notes = Note.query.filter_by(user_id=user_id)\
                                .order_by(Note.created_at.desc())\
                                .limit(5).all()
        
        return jsonify({
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks,
                'recent': [task.to_dict() for task in recent_tasks]
            },
            'goals': {
                'total': total_goals,
                'active': active_goals,
                'completed': completed_goals
            },
            'notes': {
                'total': total_notes,
                'text': text_notes,
                'voice': voice_notes,
                'recent': [note.to_dict() for note in recent_notes]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

