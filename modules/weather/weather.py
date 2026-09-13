"""Weather intelligence module. Uses Open-Meteo (free, no API key required)."""
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_recommendation(lat, lon):
    if lat is None or lon is None:
        return {"error": "Latitude/longitude not provided."}

    try:
        resp = requests.get(OPEN_METEO_URL, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,precipitation,relative_humidity_2m",
            "daily": "precipitation_probability_max",
            "timezone": "auto",
        }, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": f"Weather service unavailable: {e}"}
    except ValueError:
        return {"error": "Weather service returned an unreadable response."}

    current = data.get("current", {})
    rain_prob = data.get("daily", {}).get("precipitation_probability_max", [None])[0]
    humidity = current.get("relative_humidity_2m")

    advice = []
    if humidity is not None and humidity > 80:
        advice.append("High humidity increases fungal disease risk. Monitor plants closely.")
    if rain_prob is not None and rain_prob > 70:
        advice.append("High rain probability today. Consider delaying pesticide spraying.")

    return {
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": humidity,
        "rain_probability_pct": rain_prob,
        "advice": advice or ["No immediate weather-related risk detected."],
    }
