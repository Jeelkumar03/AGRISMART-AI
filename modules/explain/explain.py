"""Grounded, plain-language explanation + actionable advice using Gemini.

The prompt strictly instructs the model to use only the facts it is given
and not invent new diagnoses, numbers, or treatment specifics. This keeps
the output grounded in the backend's own computed results instead of
free-form generation -- the model interprets data it's handed, it doesn't
originate new claims.
"""
import json
import os
import re

import requests

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def _extract_json(text):
    """Gemini sometimes wraps JSON in ```json fences -- strip them before parsing."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def generate_explanation(crop, condition, confidence, irrigation, weather, sustainability, language="English"):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Explanation feature not configured (missing GEMINI_API_KEY)."}

    prompt = f"""You are helping a farmer understand a crop diagnosis result and know what to do next.
Use ONLY the facts listed below. Do not invent any additional facts, numbers, or diagnoses.

Diagnosis: {crop} - {condition} ({confidence:.0f}% confidence)
Irrigation advice: {irrigation.get('action')} - {irrigation.get('reason')}
Weather: {weather.get('temperature_c')}C, {weather.get('humidity_pct')}% humidity, {weather.get('rain_probability_pct')}% rain chance
Sustainability score: {sustainability.get('score')}/100

Respond entirely in {language}. Respond with ONLY valid JSON, no markdown formatting, in this exact shape:
{{"explanation": "3-4 sentence plain-language summary of what these results mean, written in {language}", "next_steps": ["short actionable step in {language}", "short actionable step in {language}", "short actionable step in {language}"]}}

Each step must be under 15 words, concrete, and doable today. Do not suggest
specific pesticide brands, chemicals, or dosages -- keep steps at the level
of general practice (e.g. "isolate affected plants", "avoid overhead
watering this week")."""

    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = _extract_json(text)
        return {
            "explanation": (parsed.get("explanation") or "").strip(),
            "next_steps": parsed.get("next_steps") or [],
        }
    except requests.RequestException as e:
        return {"error": f"Explanation service unavailable: {e}"}
    except (KeyError, IndexError, json.JSONDecodeError):
        return {"error": "Explanation service returned an unexpected response."}
