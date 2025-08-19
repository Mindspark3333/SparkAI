from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..database.db_session import get_db
from ..models.user import User

user_settings_bp = Blueprint("user_settings", __name__)


@user_settings_bp.route("/user/settings/<int:user_id>", methods=["GET"])
def get_user_settings(user_id):
    """
    Retrieve settings/preferences for a given user.
    """
    db: Session = get_db()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "email": user.email,
            "preferences": user.preferences or {}
        }), 200
    finally:
        db.close()


@user_settings_bp.route("/user/settings/<int:user_id>", methods=["PUT"])
def update_user_settings(user_id):
    """
    Update settings/preferences for a given user.
    Request JSON: { "preferences": { ... } }
    """
    data = request.json
    preferences = data.get("preferences")

    if preferences is None:
        return jsonify({"error": "Missing preferences"}), 400

    db: Session = get_db()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.preferences = preferences
        db.commit()

        return jsonify({
            "message": "Preferences updated",
            "preferences": user.preferences
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()