"""Confirms Python, libraries, and the dataset path all work together.

Usage:
    python test_setup.py
"""
from pathlib import Path

from PIL import Image

DATA_DIR = Path("data/train")


def main():
    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found. Put your dataset in data/train/<class_name>/*.jpg")
        return

    class_dirs = [p for p in DATA_DIR.iterdir() if p.is_dir()]
    if not class_dirs:
        print(f"ERROR: no class subfolders found inside {DATA_DIR}")
        return

    sample_image = next(class_dirs[0].glob("*.*"), None)
    if sample_image is None:
        print(f"ERROR: no images found inside {class_dirs[0]}")
        return

    img = Image.open(sample_image)
    print("Setup OK.")
    print(f"Found {len(class_dirs)} classes.")
    print(f"Sample image: {sample_image.name}, size={img.size}, mode={img.mode}")


if __name__ == "__main__":
    main()
