"""Evaluate a trained model on the validation set.

Usage:
    python evaluate.py --model experiments/experiment_001/best_model.pth
"""
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from preprocessing import get_dataloaders
from train import DEVICE, build_model


def evaluate(model_path, classes_path, data_dir="data", out_dir=None):
    with open(classes_path) as f:
        classes = json.load(f)

    _, val_loader, _ = get_dataloaders(data_dir)

    model = build_model(len(classes))
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(DEVICE)
            preds = model(images).argmax(dim=1).cpu().tolist()
            all_preds.extend(preds)
            all_labels.extend(labels.tolist())

    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro")
    precision = precision_score(all_labels, all_preds, average="macro", zero_division=0)
    recall = recall_score(all_labels, all_preds, average="macro", zero_division=0)
    cm = confusion_matrix(all_labels, all_preds)
    report = classification_report(all_labels, all_preds, target_names=classes, zero_division=0)

    print("\nModel Evaluation")
    print("-" * 40)
    print(f"Accuracy       : {acc * 100:.2f}%")
    print(f"Macro-F1       : {macro_f1 * 100:.2f}%")
    print(f"Precision      : {precision * 100:.2f}%")
    print(f"Recall         : {recall * 100:.2f}%")
    print("\nPer-class report:\n", report)

    out_dir = Path(out_dir or Path(model_path).parent)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "eval_metrics.json", "w") as f:
        json.dump({
            "accuracy": acc,
            "macro_f1": macro_f1,
            "precision": precision,
            "recall": recall,
        }, f, indent=2)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    fig, ax = plt.subplots(figsize=(8, 8))
    disp.plot(ax=ax, xticks_rotation=90, cmap="Blues", colorbar=False)
    plt.tight_layout()
    plt.savefig(out_dir / "confusion_matrix.png")
    print(f"\nSaved metrics + confusion matrix to {out_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="experiments/experiment_001/best_model.pth")
    parser.add_argument("--classes", type=str, default="experiments/experiment_001/classes.json")
    parser.add_argument("--data_dir", type=str, default="data")
    args = parser.parse_args()
    evaluate(args.model, args.classes, args.data_dir)
