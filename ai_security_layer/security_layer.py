import os
import pickle
from .config import CONFIDENCE_THRESHOLD, DANGEROUS_KEYWORDS

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
_model = None
_vectorizer = None

def load_artifacts():
    global _model, _vectorizer
    
    if _model is None or _vectorizer is None:
        base_dir = os.path.dirname(__file__)
        
        with open(os.path.join(base_dir, "model.pkl"), "rb") as f:
            _model = pickle.load(f)
        
        with open(os.path.join(base_dir, "vectorizer.pkl"), "rb") as f:
            _vectorizer = pickle.load(f)
        
        print("[DEBUG] Model and vectorizer loaded")

    return _model, _vectorizer

def predict_prompt(prompt):
    model, vectorizer = load_artifacts()

    X = vectorizer.transform([prompt])

    prediction = model.predict(X)[0]

    if hasattr(model, "predict_proba"):
        confidence = max(model.predict_proba(X)[0])
    else:
        confidence = -1.0
    return prediction, confidence
# # 🔥 Mock ML model (replace later with your trained model)
# def predict_prompt(prompt):
#     prompt_lower = prompt.lower()

#     # Simulated ML behavior
#     if any(word in prompt_lower for word in ["delete", "sudo", "passwd"]):
#         return "DANGEROUS", 0.9
#     else:
#         return "SAFE", 0.9


# 🔐 Hybrid Security Check
def security_check(prompt):
    prompt_lower = prompt.lower()

    # Rule-based layer FIRST (strong protection)
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in prompt_lower:
            return {
                "label": "DANGEROUS",
                "confidence": 1.0,
                "source": "RULE_BASED"
            }

    # ML layer
    label, confidence = predict_prompt(prompt)

    # Confidence handling
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "label": "UNCERTAIN",
            "confidence": confidence,
            "source": "ML_LOW_CONF"
        }

    return {
        "label": label,
        "confidence": confidence,
        "source": "ML"
    }