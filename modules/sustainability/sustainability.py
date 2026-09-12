"""Transparent, reproducible sustainability scoring.

The formula and weights are intentionally simple and documented so the score
is explainable, not a black box. Replace the placeholder sub-scores with real
signals (pesticide use, water logs, etc.) as your data allows.
"""

WEIGHTS = {"crop_health": 0.5, "water_efficiency": 0.3, "resource_usage": 0.2}


def _is_healthy(disease):
    # Class names follow "<Crop>___healthy" (e.g. "Tomato___healthy"), not a bare "healthy".
    return "healthy" in (disease or "").lower()


def compute_sustainability_score(disease, irrigation, weather):
    crop_health = 100 if _is_healthy(disease) else 60
    water_efficiency = 100 if (irrigation or {}).get("action") == "DELAY IRRIGATION" else 70
    resource_usage = 80  # placeholder baseline

    score = (
        crop_health * WEIGHTS["crop_health"]
        + water_efficiency * WEIGHTS["water_efficiency"]
        + resource_usage * WEIGHTS["resource_usage"]
    )

    return {
        "score": round(score, 1),
        "breakdown": {
            "crop_health": crop_health,
            "water_efficiency": water_efficiency,
            "resource_usage": resource_usage,
        },
        "weights": WEIGHTS,
    }