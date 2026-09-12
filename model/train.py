"""Train a transfer-learning disease classifier (two-stage: frozen head, then fine-tune).

Usage:
    python train.py --stage1-epochs 5 --stage2-epochs 30 --lr 1e-3 --fine-tune-lr 1e-4
"""
import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.optim import Adam
from torchvision import models

from preprocessing import get_dataloaders

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_model(num_classes, freeze_backbone=True):
    """MobileNetV3-Large: lightweight, pretrained on ImageNet, good starting point."""
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
    for param in model.features.parameters():
        param.requires_grad = not freeze_backbone
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model.to(DEVICE)


def unfreeze_backbone(model) -> None:
    for param in model.features.parameters():
        param.requires_grad = True


def run_epoch(model, loader, criterion, optimizer=None):
    """One pass over loader. Pass optimizer to train; omit it to evaluate."""
    train_mode = optimizer is not None
    model.train(train_mode)
    total_loss = 0.0
    all_preds, all_labels = [], []

    context = torch.enable_grad() if train_mode else torch.no_grad()
    with context:
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            if train_mode:
                optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            if train_mode:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * images.size(0)
            all_preds.extend(outputs.argmax(dim=1).cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    avg_loss = total_loss / len(loader.dataset)
    macro_f1 = f1_score(all_labels, all_preds, average="macro")
    return avg_loss, macro_f1


def train_stage(model, train_loader, val_loader, criterion, optimizer, epochs, patience,
                 best_f1, out_dir, classes, history, stage_name):
    """Run one training stage; stop early if val macro-F1 stalls for `patience` epochs."""
    epochs_without_improvement = 0

    for epoch in range(1, epochs + 1):
        train_loss, train_f1 = run_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_f1 = run_epoch(model, val_loader, criterion)

        print(f"[{stage_name}] epoch {epoch}/{epochs} | "
              f"train_loss={train_loss:.4f} train_f1={train_f1:.4f} | "
              f"val_loss={val_loss:.4f} val_f1={val_f1:.4f}")

        history.append({
            "stage": stage_name, "epoch": epoch,
            "train_loss": train_loss, "train_macro_f1": train_f1,
            "val_loss": val_loss, "val_macro_f1": val_f1,
        })

        if val_f1 > best_f1:
            best_f1 = val_f1
            epochs_without_improvement = 0
            torch.save(model.state_dict(), Path(out_dir) / "best_model.pth")
            with open(Path(out_dir) / "classes.json", "w") as f:
                json.dump(classes, f)
            print(f"  -> new best (val_macro_f1={best_f1:.4f}), checkpoint saved")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                print(f"  -> no improvement for {patience} epochs, stopping {stage_name} early")
                break

    return best_f1


def train(stage1_epochs=5, stage2_epochs=30, lr=1e-3, fine_tune_lr=1e-4,
          patience=5, seed=42, data_dir="data", out_dir="experiments/experiment_001"):
    set_seed(seed)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    train_loader, val_loader, classes = get_dataloaders(data_dir)
    criterion = nn.CrossEntropyLoss()
    history = []
    best_f1 = 0.0

    # Stage 1: frozen backbone, train the classifier head only (fast sanity-check pass).
    model = build_model(len(classes), freeze_backbone=True)
    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)
    best_f1 = train_stage(model, train_loader, val_loader, criterion, optimizer,
                           stage1_epochs, patience, best_f1, out_dir, classes, history, "stage1-frozen")

    # Stage 2: unfreeze the backbone, fine-tune the whole network at a lower LR.
    unfreeze_backbone(model)
    optimizer = Adam(model.parameters(), lr=fine_tune_lr)
    best_f1 = train_stage(model, train_loader, val_loader, criterion, optimizer,
                           stage2_epochs, patience, best_f1, out_dir, classes, history, "stage2-finetune")

    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump({"history": history, "best_val_macro_f1": best_f1}, f, indent=2)

    print(f"\nBest val macro-F1: {best_f1:.4f}. Weights saved to {out_dir}/best_model.pth")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-epochs", type=int, default=5, help="epochs with frozen backbone")
    parser.add_argument("--stage2-epochs", type=int, default=30, help="max epochs after unfreezing")
    parser.add_argument("--lr", type=float, default=1e-3, help="learning rate for stage 1 (head only)")
    parser.add_argument("--fine-tune-lr", type=float, default=1e-4, help="learning rate for stage 2 (full network)")
    parser.add_argument("--patience", type=int, default=5, help="stop a stage early after this many non-improving epochs")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--out_dir", type=str, default="experiments/experiment_001")
    args = parser.parse_args()
    train(args.stage1_epochs, args.stage2_epochs, args.lr, args.fine_tune_lr,
          args.patience, args.seed, args.data_dir, args.out_dir)