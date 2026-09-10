"""Basic edge-case tests. Run with: pytest tests/"""
import io
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "model"))

import pytest
from PIL import Image


def test_corrupted_image_raises():
    corrupted = io.BytesIO(b"not an image")
    with pytest.raises(Exception):
        Image.open(corrupted).convert("RGB")


def test_predict_skips_without_trained_model():
    model_path = Path("experiments/experiment_001/best_model.pth")
    if not model_path.exists():
        pytest.skip("No trained model yet -- train.py must run first.")
