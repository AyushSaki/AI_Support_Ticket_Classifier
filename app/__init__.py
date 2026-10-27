# AI Support Ticket Classifier Flask App
from flask import Flask
import os

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )
    app.config["SECRET_KEY"] = "ticketai-secret-change-in-production-2024"
    app.config["CONFIDENCE_THRESHOLD"] = 0.45

    # Demo users (username → password)
    # In production use a real database + hashed passwords
    app.config["USERS"] = {
        "admin": "admin123",
        "agent": "agent123",
        "demo": "demo123",
    }

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
