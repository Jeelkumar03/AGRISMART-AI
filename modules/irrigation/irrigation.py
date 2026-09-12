"""Deterministic, rule-based irrigation recommendation."""

SOIL_MOISTURE_THRESHOLD = 35  # below this %, irrigation is generally needed
RAIN_PROBABILITY_THRESHOLD = 70  # above this %, delay irrigation


def get_irrigation_recommendation(soil_moisture_pct, weather=None):
    """Return an irrigation action + human-readable reason.

    soil_moisture_pct: 0-100. None or out-of-range values return an error dict
    instead of a recommendation, so the caller can show a clear message rather
    than acting on bad sensor data.
    """
    if soil_moisture_pct is None or not (0 <= soil_moisture_pct <= 100):
        return {
            "action": "UNKNOWN",
            "reason": f"Invalid soil moisture reading: {soil_moisture_pct!r}. Expected 0-100.",
        }

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