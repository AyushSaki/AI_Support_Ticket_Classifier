"""
Predictor module: loads the trained TF-IDF + LogisticRegression pipeline
and provides prediction with top-k results and confidence.
"""
import os
import json
import joblib
import numpy as np
from pathlib import Path

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "support_ticket_classifier"
CONFIG_DIR = PROJECT_ROOT / "config"

_pipeline = None
_label_encoder = None
_labels = None


def load_model():
    """Lazy-load the model and label encoder once."""
    global _pipeline, _label_encoder, _labels
    if _pipeline is None:
        pipeline_path = MODEL_DIR / "pipeline.joblib"
        le_path = MODEL_DIR / "label_encoder.joblib"
        labels_path = MODEL_DIR / "labels.json"

        if not pipeline_path.exists():
            raise FileNotFoundError(
                f"Model not found at {pipeline_path}. "
                "Please run the training notebook first."
            )

        _pipeline = joblib.load(pipeline_path)
        _label_encoder = joblib.load(le_path)

        with open(labels_path, "r") as f:
            _labels = json.load(f)

    return _pipeline, _label_encoder, _labels


def predict(text: str, top_k: int = 3, confidence_threshold: float = 0.45):
    """
    Predict the intent for a customer support ticket.

    Args:
        text: The raw ticket / query text.
        top_k: Number of top predictions to return.
        confidence_threshold: If top confidence is below this, flag for human review.

    Returns:
        dict with:
            - intent: predicted label (str)
            - confidence: float (0-1)
            - confidence_pct: str like "74.4%"
            - top_k: list of {intent, confidence, confidence_pct}
            - needs_human_review: bool
            - model_type: str
    """
    if not text or not text.strip():
        return {
            "error": "Empty text provided",
            "intent": None,
            "confidence": 0.0,
            "needs_human_review": True,
        }

    pipeline, le, labels = load_model()

    # Predict
    proba = pipeline.predict_proba([text.strip()])[0]
    top_indices = np.argsort(proba)[::-1][:top_k]

    top_results = []
    for idx in top_indices:
        conf = float(proba[idx])
        top_results.append(
            {
                "intent": labels[idx],
                "confidence": conf,
                "confidence_pct": f"{conf * 100:.1f}%",
            }
        )

    best = top_results[0]
    needs_review = best["confidence"] < confidence_threshold

    return {
        "intent": best["intent"],
        "confidence": best["confidence"],
        "confidence_pct": best["confidence_pct"],
        "top_k": top_results,
        "needs_human_review": needs_review,
        "model_type": "TF-IDF + LogisticRegression",
        "text": text.strip(),
    }


def get_metrics():
    """Return saved evaluation metrics if available."""
    metrics_path = MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)
    return None


def get_all_labels():
    """Return the full list of 77 intent labels."""
    _, _, labels = load_model()
    return labels
