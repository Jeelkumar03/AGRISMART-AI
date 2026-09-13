"""Print the top-5 predicted classes with confidence for a single image.

Usage:
    python -m model.diagnose --image path/to/photo.jpg
"""
import argparse
import json

import torch
import torch.nn.functional as F
from PIL import Image

from preprocessing import EVAL_TRANSFORMS
from train import DEVICE, build_model

MODEL_PATH = "experiments/experiment_001/best_model.pth"
CLASSES_PATH = "experiments/experiment_001/classes.json"


def top5(image_path):
    with open(CLASSES_PATH) as f:
        classes = json.load(f)
    model = build_model(len(classes))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()

    image = Image.open(image_path).convert("RGB")
    tensor = EVAL_TRANSFORMS(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        probs = F.softmax(model(tensor), dim=1)[0]

    top_probs, top_idx = probs.topk(5)
    for p, i in zip(top_probs, top_idx):
        print(f"{classes[i]:50s} {p.item() * 100:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    top5(args.image)
