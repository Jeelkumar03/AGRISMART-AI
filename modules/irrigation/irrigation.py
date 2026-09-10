"""Deterministic, rule-based irrigation recommendation."""

SOIL_MOISTURE_THRESHOLD = 35  # below this %, irrigation is generally needed
RAIN_PROBABILITY_THRESHOLD = 70  # above this %, delay irrigation


def get_irrigation_recommendation(soil_moisture_pct, weather=None):
    rain_prob = None
    if weather and not weather.get("error"):
        rain_prob = weather.get("rain_probability_pct")

    if rain_prob is not None and rain_prob >= RAIN_PROBABILITY_THRESHOLD:
        return {
            "action": "DELAY IRRIGATION",
            "reason": f"Rain probability is {rain_prob}%, likely to naturally water the field.",
        }

    if soil_moisture_pct < SOIL_MOISTURE_THRESHOLD:
        return {
            "action": "IRRIGATE",
            "reason": f"Soil moisture ({soil_moisture_pct}%) is below the {SOIL_MOISTURE_THRESHOLD}% threshold.",
        }

    return {
        "action": "DELAY IRRIGATION",
        "reason": f"Soil moisture ({soil_moisture_pct}%) is adequate.",
    }
