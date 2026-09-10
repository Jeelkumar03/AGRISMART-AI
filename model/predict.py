"""Predict the disease class for a single image.

Usage:
    python predict.py --image sample.jpg
"""
import argparse
import json

import torch
import torch.nn.functional as F
from PIL import Image

from preprocessing import EVAL_TRANSFORMS
from train import DEVICE, build_model

# Below this confidence, don't state a disease as fact -- flag it as uncertain instead.
CONFIDENCE_THRESHOLD = 0.5


def load_model(model_path, classes_path):
    with open(classes_path) as f:
        classes = json.load(f)
    model = build_model(len(classes))
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.eval()
    return model, classes


def predict(image_path, model, classes, threshold=CONFIDENCE_THRESHOLD):
    image = Image.open(image_path).convert("RGB")
    tensor = EVAL_TRANSFORMS(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        probs = F.softmax(model(tensor), dim=1)[0]
        confidence, idx = probs.max(dim=0)

    label = classes[idx.item()]
    confidence = confidence.item()

    if confidence < threshold:
        return {"disease": "Uncertain", "confidence": confidence, "raw_prediction": label}
    return {"disease": label, "confidence": confidence}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True)
    parser.add_argument("--model", type=str, default="experiments/experiment_001/best_model.pth")
    parser.add_argument("--classes", type=str, default="experiments/experiment_001/classes.json")
    args = parser.parse_args()

    model, classes = load_model(args.model, args.classes)
    result = predict(args.image, model, classes)

    print(f"Disease: {result['disease']}")
    print(f"Confidence: {result['confidence'] * 100:.1f}%")
