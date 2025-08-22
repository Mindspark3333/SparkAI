from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# ---- Database config ---------------------------------------------------------
# On App Engine Standard the filesystem is read-only except /tmp.
# Use /tmp/app.db there; use app.db in the repo for local dev.
if os.getenv("GAE_ENV", "").startswith("standard"):
    db_path = os.path.join("/tmp", "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---- Models ------------------------------------------------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="open")  # open | in_progress | done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.Integer, default=0)  # 0..100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
        }

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }

# Create tables on first request (works under Gunicorn)
@app.before_first_request
def init_db():
    db.create_all()

# ---- Endpoints ---------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "service": "Master Agent Backend",
        "status": "running",
        "version": "phase-1"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

# Chat (simple echo for now)
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    return jsonify({"response": f"You said: {data.get('message', '')}"})

# Tasks
@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    return jsonify([t.to_dict() for t in Task.query.order_by(Task.created_at.desc()).all()])

@app.route("/api/tasks", methods=["POST"])
def create_task():
    d = request.get_json(silent=True) or {}
    t = Task(
        title=d.get("title", "Untitled"),
        description=d.get("description", ""),
        status=d.get("status", "open"),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

# Goals
@app.route("/api/goals", methods=["GET"])
def list_goals():
    return jsonify([g.to_dict() for g in Goal.query.order_by(Goal.created_at.desc()).all()])

@app.route("/api/goals", methods=["POST"])
def create_goal():
    d = request.get_json(silent=True) or {}
    g = Goal(
        title=d.get("title", "New Goal"),
        progress=int(d.get("progress", 0)),
    )
    db.session.add(g)
    db.session.commit()
    return jsonify(g.to_dict()), 201

# Notes (text only in Phase 1)
@app.route("/api/notes", methods=["GET"])
def list_notes():
    return jsonify([n.to_dict() for n in Note.query.order_by(Note.created_at.desc()).all()])

@app.route("/api/notes", methods=["POST"])
def create_note():
    d = request.get_json(silent=True) or {}
    n = Note(text=d.get("text", ""))
    db.session.add(n)
    db.session.commit()
    return jsonify(n.to_dict()), 201

# Dashboard counts
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    return jsonify({
        "tasks": Task.query.count(),
        "goals": Goal.query.count(),
        "notes": Note.query.count()
    })

# No app.run(); Gunicorn starts the app in App Engine