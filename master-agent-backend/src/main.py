from flask import Flask
from flask_cors import CORS
from .routes.research import research_bp
from .routes.user_settings import user_settings_bp
from .database.db_session import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Initialize database
    init_db()

    # Register blueprints
    app.register_blueprint(research_bp, url_prefix="/api")
    app.register_blueprint(user_settings_bp, url_prefix="/api")

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)