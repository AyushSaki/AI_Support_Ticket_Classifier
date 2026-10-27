"""
AI Support Ticket Classifier – Flask entry point
Run: python app.py
Then open http://127.0.0.1:5003
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Default to 5003 to avoid macOS AirPlay conflict on 5000
    app.run(host="0.0.0.0", port=5003, debug=True)
