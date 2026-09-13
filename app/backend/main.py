"""Minimal backend API wrapping the disease classifier + bonus modules.

Run from the project root:
    python app/backend/main.py
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "model"))
sys.path.append(str(ROOT))

from flask import Flask, jsonify, request  # noqa: E402
from flask_cors import CORS  # noqa: E402

from modules.irrigation.irrigation import get_irrigation_recommendation  # noqa: E402
from modules.sustainability.sustainability import compute_sustainability_score  # noqa: E402
from modules.weather.weather import get_weather_recommendation  # noqa: E402
from predict import load_model  # noqa: E402
from predict import predict as predict_disease  # noqa: E402

app = Flask(__name__)
CORS(app)

MODEL_PATH = str(ROOT / "experiments/experiment_001/best_model.pth")
CLASSES_PATH = str(ROOT / "experiments/experiment_001/classes.json")
_model, _classes = None, None


def get_model():
    global _model, _classes
    if _model is None:
        _model, _classes = load_model(MODEL_PATH, CLASSES_PATH)
    return _model, _classes


@app.route("/predict", methods=["POST"])
def predict_route():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    tmp_path = str(Path(tempfile.gettempdir()) / "upload.jpg")
    file.save(tmp_path)

    try:
        model, classes = get_model()
        result = predict_disease(tmp_path, model, classes)
    except FileNotFoundError:
        return jsonify({"error": "Model not trained yet. Run train.py first."}), 503
    except (OSError, ValueError):
        return jsonify({"error": "Uploaded file is not a valid image."}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500

    return jsonify(result)


@app.route("/recommendation", methods=["POST"])
def recommendation_route():
    """Combines disease result + weather + irrigation + sustainability into one response."""
    data = request.get_json(force=True) or {}
    disease = data.get("disease")
    lat, lon = data.get("lat"), data.get("lon")
    soil_moisture = data.get("soil_moisture", 40)

    weather = get_weather_recommendation(lat, lon) if lat and lon else None
    irrigation = get_irrigation_recommendation(soil_moisture, weather)
    sustainability = compute_sustainability_score(disease, irrigation, weather)

    return jsonify({
        "disease": disease,
        "weather": weather,
        "irrigation": irrigation,
        "sustainability": sustainability,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)
