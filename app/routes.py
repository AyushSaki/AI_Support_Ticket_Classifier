"""
Flask routes – Login, Home, Classifier, Chatbot, API
"""
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
    session,
    redirect,
    url_for,
)
from functools import wraps
from .predictor import predict, get_metrics, get_all_labels
from .chatbot import get_bot_reply
from datetime import datetime
import secrets

main_bp = Blueprint("main", __name__)

PREDICTION_HISTORY = []
CHAT_HISTORY = {}  # session_id -> list of messages
MAX_HISTORY = 80


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("main.login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def _session_id():
    if "sid" not in session:
        session["sid"] = secrets.token_hex(8)
    return session["sid"]


# ─────────────────────────── Auth ───────────────────────────

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("main.home"))

    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        users = current_app.config.get("USERS", {})

        if username in users and users[username] == password:
            session["user"] = username
            session.permanent = True
            next_url = request.args.get("next") or url_for("main.home")
            return redirect(next_url)
        error = "Invalid username or password"

    return render_template("login.html", error=error)


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


# ─────────────────────────── Pages ───────────────────────────

@main_bp.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("main.home"))
    return redirect(url_for("main.login"))


@main_bp.route("/home")
@login_required
def home():
    metrics = get_metrics()
    labels = get_all_labels()
    recent = PREDICTION_HISTORY[:5]
    return render_template(
        "home.html",
        user=session["user"],
        metrics=metrics,
        num_labels=len(labels),
        recent=recent,
    )


@main_bp.route("/classify")
@login_required
def classify_page():
    metrics = get_metrics()
    labels = get_all_labels()
    return render_template(
        "classify.html",
        user=session["user"],
        metrics=metrics,
        num_labels=len(labels),
        history=PREDICTION_HISTORY[:12],
        threshold=current_app.config.get("CONFIDENCE_THRESHOLD", 0.45),
    )


@main_bp.route("/chatbot")
@login_required
def chatbot_page():
    sid = _session_id()
    history = CHAT_HISTORY.get(sid, [])
    return render_template(
        "chatbot.html",
        user=session["user"],
        history=history,
    )


@main_bp.route("/history")
@login_required
def history_page():
    return render_template(
        "history.html",
        user=session["user"],
        history=PREDICTION_HISTORY[:50],
    )


# ─────────────────────────── API ───────────────────────────

@main_bp.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or data.get("ticket") or ""
    top_k = int(data.get("top_k", 3))
    threshold = float(
        data.get("confidence_threshold", current_app.config.get("CONFIDENCE_THRESHOLD", 0.45))
    )
    result = predict(text, top_k=top_k, confidence_threshold=threshold)

    if "error" not in result:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": session.get("user"),
            "text": result.get("text", text)[:220],
            "intent": result["intent"],
            "confidence_pct": result["confidence_pct"],
            "needs_human_review": result["needs_human_review"],
        }
        PREDICTION_HISTORY.insert(0, entry)
        if len(PREDICTION_HISTORY) > MAX_HISTORY:
            PREDICTION_HISTORY.pop()

    return jsonify(result)


@main_bp.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    threshold = current_app.config.get("CONFIDENCE_THRESHOLD", 0.45)

    bot = get_bot_reply(message, confidence_threshold=threshold)

    sid = _session_id()
    if sid not in CHAT_HISTORY:
        CHAT_HISTORY[sid] = []

    CHAT_HISTORY[sid].append({
        "role": "user",
        "text": message,
        "time": datetime.now().strftime("%H:%M"),
    })
    CHAT_HISTORY[sid].append({
        "role": "bot",
        "text": bot["reply"],
        "intent": bot.get("intent"),
        "confidence_pct": bot.get("confidence_pct"),
        "time": datetime.now().strftime("%H:%M"),
    })
    CHAT_HISTORY[sid] = CHAT_HISTORY[sid][-40:]

    return jsonify(bot)


@main_bp.route("/api/labels")
@login_required
def api_labels():
    labels = get_all_labels()
    return jsonify({"labels": labels, "count": len(labels)})


@main_bp.route("/api/metrics")
@login_required
def api_metrics():
    metrics = get_metrics()
    if metrics is None:
        return jsonify({"error": "Metrics not available"}), 404
    return jsonify(metrics)


@main_bp.route("/api/history")
@login_required
def api_history():
    return jsonify({"history": PREDICTION_HISTORY, "count": len(PREDICTION_HISTORY)})


@main_bp.route("/health")
def health():
    try:
        get_all_labels()
        return jsonify({"status": "ok", "model_loaded": True})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
