"""Train a transfer-learning disease classifier.

Usage:
    python train.py --epochs 10 --lr 1e-4
"""
import argparse
import json
from pathlib import Path

import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.optim import Adam
from torchvision import models

from preprocessing import get_dataloaders

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model(num_classes):
    """MobileNetV3-Large: lightweight, pretrained on ImageNet, good starting point."""
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
    # Freeze the backbone so we only train the final classification head at first.
    for param in model.features.parameters():
        param.requires_grad = False
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model.to(DEVICE)


def evaluate_epoch(model, loader):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            preds = model(images).argmax(dim=1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())
    return f1_score(all_labels, all_preds, average="macro")


def train(epochs=10, lr=1e-4, data_dir="data", out_dir="experiments/experiment_001"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    train_loader, val_loader, classes = get_dataloaders(data_dir)
    model = build_model(len(classes))

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)

    best_f1 = 0.0
    history = []

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)

        train_loss = running_loss / len(train_loader.dataset)
        val_f1 = evaluate_epoch(model, val_loader)
        print(f"Epoch {epoch + 1}/{epochs} | train_loss={train_loss:.4f} | val_macro_f1={val_f1:.4f}")
        history.append({"epoch": epoch + 1, "train_loss": train_loss, "val_macro_f1": val_f1})

        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(model.state_dict(), Path(out_dir) / "best_model.pth")
            with open(Path(out_dir) / "classes.json", "w") as f:
                json.dump(classes, f)

    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump({"history": history, "best_val_macro_f1": best_f1}, f, indent=2)

    print(f"\nBest val macro-F1: {best_f1:.4f}. Weights saved to {out_dir}/best_model.pth")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--out_dir", type=str, default="experiments/experiment_001")
    args = parser.parse_args()
    train(args.epochs, args.lr, args.data_dir, args.out_dir)
