from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# DB config: SQLite locally, Cloud SQL later
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ----------------- Models -----------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Init DB
@app.before_first_request
def init_db():
    db.create_all()

# ----------------- Endpoints -----------------
@app.route("/")
def home():
    return jsonify({"service": "Master Agent Backend", "status": "running", "version": "phase-1"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    return jsonify({"response": f"You said: {data.get('message','')}"})

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    return jsonify([t.to_dict() for t in Task.query.all()])

@app.route("/api/tasks", methods=["POST"])
def create_task():
    d = request.get_json() or {}
    t = Task(title=d.get("title","Untitled"), description=d.get("description",""))
    db.session.add(t); db.session.commit()
    return jsonify(t.to_dict()), 201

@app.route("/api/goals", methods=["GET"])
def list_goals():
    return jsonify([g.to_dict() for g in Goal.query.all()])

@app.route("/api/goals", methods=["POST"])
def create_goal():
    d = request.get_json() or {}
    g = Goal(title=d.get("title","New Goal"), progress=int(d.get("progress",0)))
    db.session.add(g); db.session.commit()
    return jsonify(g.to_dict()), 201

@app.route("/api/notes", methods=["GET"])
def list_notes():
    return jsonify([n.to_dict() for n in Note.query.all()])

@app.route("/api/notes", methods=["POST"])
def create_note():
    d = request.get_json() or {}
    n = Note(text=d.get("text",""))
    db.session.add(n); db.session.commit()
    return jsonify(n.to_dict()), 201

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    return jsonify({
        "tasks": Task.query.count(),
        "goals": Goal.query.count(),
        "notes": Note.query.count()
    })