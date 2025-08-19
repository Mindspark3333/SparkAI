from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..utils.content_extractor import ContentExtractor
from ..utils.gemini_analyzer import GeminiAnalyzer
from ..models.research_result import ResearchResult
from ..database.db_session import get_db
from ..models.user import User

research_bp = Blueprint("research", __name__)
extractor = ContentExtractor()
analyzer = GeminiAnalyzer()


@research_bp.route("/research/submit", methods=["POST"])
def submit_research():
    """
    Accepts a URL or uploaded file, extracts content, and queues for analysis.
    Request JSON: { "url": "https://example.com/article" }
    """
    data = request.json
    url = data.get("url")
    user_id = data.get("user_id")

    if not url or not user_id:
        return jsonify({"error": "Missing required fields"}), 400

    db: Session = get_db()
    try:
        extracted = extractor.extract(url)
        enriched = analyzer.analyze_url_content(extracted)

        result = ResearchResult(
            user_id=user_id,
            source_url=url,
            source_type="web",
            title=enriched.get("title"),
            raw_text=enriched.get("raw_text"),
            content_summary=enriched.get("content_summary"),
            key_points=enriched.get("key_points"),
            sentiment=enriched.get("sentiment"),
            category=enriched.get("category"),
            importance_score=enriched.get("importance_score"),
            tags=enriched.get("tags"),
        )
        db.add(result)
        db.commit()

        return jsonify(result.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@research_bp.route("/research/list/<int:user_id>", methods=["GET"])
def list_research(user_id):
    """
    Returns all research results for a given user.
    """
    db: Session = get_db()
    try:
        results = db.query(ResearchResult).filter_by(user_id=user_id).all()
        return jsonify([r.to_dict() for r in results]), 200
    finally:
        db.close()


@research_bp.route("/research/<int:research_id>", methods=["GET"])
def get_research(research_id):
    """
    Retrieve a single research result by ID.
    """
    db: Session = get_db()
    try:
        result = db.query(ResearchResult).filter_by(id=research_id).first()
        if not result:
            return jsonify({"error": "Not found"}), 404
        return jsonify(result.to_dict()), 200
    finally:
        db.close()