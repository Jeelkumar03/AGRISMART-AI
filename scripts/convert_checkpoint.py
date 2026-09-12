"""One-time converter: Kaggle checkpoint dict -> raw state_dict + classes.json
   expected by model/predict.py.

Run from repo root:
    python scripts/convert_checkpoint.py
"""
import json
from pathlib import Path

import torch

SRC = Path("model/checkpoints/best_model.pth")      
DEST_DIR = Path("experiments/experiment_001")

DEST_DIR.mkdir(parents=True, exist_ok=True)
checkpoint = torch.load(SRC, map_location="cpu")

torch.save(checkpoint["model_state_dict"], DEST_DIR / "best_model.pth")
with open(DEST_DIR / "classes.json", "w") as f:
    json.dump(checkpoint["classes"], f)

print(f"Done: {len(checkpoint['classes'])} classes -> {DEST_DIR}")
print(f"Val Macro-F1 was: {checkpoint['val_macro_f1']:.4f} (epoch {checkpoint['epoch']})")