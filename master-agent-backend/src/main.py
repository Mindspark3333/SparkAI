from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# --- DB config: SQLite for local dev ---
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------
# Models
# -----------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    priority = db.Column(db.String(20), default="normal")  # low | normal | high
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="open")      # open | in_progress | done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    target_date = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0)  # 0..100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
        }

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, default="")
    is_voice = db.Column(db.Boolean, default=False)
    audio_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "is_voice": self.is_voice,
            "audio_path": self.audio_path,
            "created_at": self.created_at.isoformat(),
        }

# Create tables on first request
@app.before_first_request
def _init_db():
    db.create_all()

# -----------------
# Health + banner
# -----------------
@app.route("/")
def home():
    return jsonify({"service": "Master Agent Backend", "status": "running", "version": "phase-1"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

# -----------------
# Chat (simple echo)
# -----------------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    return jsonify({"response": f"You said: {msg}"})

# -----------------
# Tasks CRUD
# -----------------
@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks])

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    t = Task(
        title=data.get("title", "Untitled Task"),
        description=data.get("description", ""),
        priority=data.get("priority", "normal"),
        due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        status=data.get("status", "open"),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    t = Task.query.get_or_404(task_id)
    return jsonify(t.to_dict())

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    t = Task.query.get_or_404(task_id)
    data = request.get_json(silent=True) or {}
    t.title = data.get("title", t.title)
    t.description = data.get("description", t.description)
    t.priority = data.get("priority", t.priority)
    t.status = data.get("status", t.status)
    if "due_date" in data:
        t.due_date = datetime.fromisoformat(data["due_date"]) if data["due_date"] else None
    db.session.commit()
    return jsonify(t.to_dict())

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"deleted": True})

# -----------------
# Goals CRUD
# -----------------
@app.route("/api/goals", methods=["GET"])
def list_goals():
    goals = Goal.query.order_by(Goal.created_at.desc()).all()
    return jsonify([g.to_dict() for g in goals])

@app.route("/api/goals", methods=["POST"])
def create_goal():
    data = request.get_json(silent=True) or {}
    g = Goal(
        title=data.get("title", "Untitled Goal"),
        description=data.get("description", ""),
        target_date=datetime.fromisoformat(data["target_date"]) if data.get("target_date") else None,
        progress=int(data.get("progress", 0)),
    )
    db.session.add(g)
    db.session.commit()
    return jsonify(g.to_dict()), 201

@app.route("/api/goals/<int:goal_id>", methods=["GET"])
def get_goal(goal_id):
    g = Goal.query.get_or_404(goal_id)
    return jsonify(g.to_dict())

@app.route("/api/goals/<int:goal_id>", methods=["PUT"])
def update_goal(goal_id):
    g = Goal.query.get_or_404(goal_id)
    data = request.get_json(silent=True) or {}
    g.title = data.get("title", g.title)
    g.description = data.get("description", g.description)
    g.progress = int(data.get("progress", g.progress))
    if "target_date" in data:
        g.target_date = datetime.fromisoformat(data["target_date"]) if data["target_date"] else None
    db.session.commit()
    return jsonify(g.to_dict())

@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    g = Goal.query.get_or_404(goal_id)
    db.session.delete(g)
    db.session.commit()
    return jsonify({"deleted": True})

# -----------------
# Notes (text now; voice later)
# -----------------
@app.route("/api/notes", methods=["GET"])
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])

@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json(silent=True) or {}
    n = Note(text=data.get("text", ""), is_voice=False)
    db.session.add(n)
    db.session.commit()
    return jsonify(n.to_dict()), 201

@app.route("/api/notes/voice", methods=["POST"])
def create_voice_note():
    # Phase 1: stub (we'll wire transcription in a later phase)
    return jsonify({"message": "Voice notes will be enabled in Phase 2"}), 501

# -----------------
# Dashboard
# -----------------
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    return jsonify({
        "tasks": Task.query.count(),
        "goals": Goal.query.count(),
        "notes": Note.query.count(),
        "recent": {
            "tasks": [t.to_dict() for t in Task.query.order_by(Task.created_at.desc()).limit(5)],
            "goals": [g.to_dict() for g in Goal.query.order_by(Goal.created_at.desc()).limit(5)],
            "notes": [n.to_dict() for n in Note.query.order_by(Note.created_at.desc()).limit(5)],
        }
    })

# No app.run(); use `flask run` locally