from .config import CONFIDENCE_THRESHOLD, DANGEROUS_KEYWORDS

# 🔥 Mock ML model (replace later with your trained model)
def predict_prompt(prompt):
    prompt_lower = prompt.lower()

    # Simulated ML behavior
    if any(word in prompt_lower for word in ["delete", "sudo", "passwd"]):
        return "DANGEROUS", 0.9
    else:
        return "SAFE", 0.9


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