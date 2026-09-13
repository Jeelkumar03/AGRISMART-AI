# AgriSmart AI

**Crop disease detection from a single leaf photo — with weather, irrigation, and sustainability guidance.**

Built by **Team Curious Coders** for Smart India Hackathon (SIH).

A farmer uploads a photo of a leaf. AgriSmart identifies the disease (or confirms the plant is healthy), checks the day's weather risk, tells them whether to irrigate, and scores the overall sustainability of the recommended action — all in a few seconds.

---

## Try it yourself

Five sample leaf photos are in [`demo_images/`](./demo_images) — pulled from our validation set (images the model never saw during training) and renamed so the disease name isn't given away. Upload `test1` through `test5` into the app and see what it predicts. Once you've tried all five, open [`demo_images/answer_key.txt`](./demo_images/answer_key.txt) to check the model's answers against the ground truth.

You're also welcome to test with your own photos. For the most reliable results:
- Use a plain-background, close-up photo of a single leaf — a reference-style photo works better than a photo of a leaf still on the plant in a field.
- Crop the image to a roughly square (1:1) frame before uploading.
- Avoid blurry, low-resolution, or screenshotted images.

The model is trained on the PlantVillage dataset, which consists of controlled, lab-condition photos. Images that match that style get the most accurate results — this is a documented limitation, not a bug. See [Known Limitations](#known-limitations).

---

## What it does

| Feature | Description |
|---|---|
| **Disease diagnosis** | Upload a leaf photo, get the disease name and a confidence score. Below 50% confidence, the app says so honestly instead of guessing. |
| **Weather risk** | Live temperature, humidity, and rain probability for the user's location, with plain-language advice (e.g. "high humidity increases fungal disease risk"). |
| **Irrigation guidance** | A simple, explainable rule combining soil moisture and rain forecast — tells the farmer whether to irrigate now or wait. |
| **Sustainability score** | A transparent 0–100 score built from crop health, water efficiency, and resource usage, with the exact weighting shown — not a black box. |
| **Accounts** | Email/password sign-up and login (Firebase Auth). Sign-up also captures the user's location, used for weather lookups. |

---

## How it works

```
┌─────────────┐      photo       ┌──────────────┐     disease      ┌─────────────────┐
│  Frontend    │ ───────────────▶ │ Flask backend │ ───────────────▶ │  MobileNetV3-L   │
│ (HTML/CSS/JS)│                  │  /predict     │                  │  classifier      │
└─────────────┘ ◀─────────────── └──────┬───────┘ ◀───────────────  └─────────────────┘
                  diagnosis              │
                                          │ disease name
                                          ▼
                                  ┌──────────────┐
                                  │ /recommendation│
                                  │  weather +    │──▶ Open-Meteo API
                                  │  irrigation + │
                                  │  sustainability│
                                  └──────────────┘
```

- **Model**: MobileNetV3-Large, transfer-learned from ImageNet weights on the [PlantVillage dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset) (`color` subset, 38 classes across 14 crops).
- **Training**: two-stage — frozen backbone first (fast head-only warm-up), then full fine-tuning at a lower learning rate, with early stopping on validation macro-F1. Trained on Kaggle's free T4×2 GPU.
- **Backend**: Flask, exposing three endpoints (below).
- **Frontend**: vanilla HTML/CSS/JS, no build step — a glassmorphism UI with Firebase email/password authentication.

---

## Model performance

| Metric | Value |
|---|---|
| Validation accuracy | 97.2% |
| Validation macro-F1 | 0.9618 |
| Best epoch | 24 |
| Classes | 38 (14 crops) |
| Validation set size | 10,861 images |

Macro-F1 (not accuracy) is the primary metric, because it weighs every class equally regardless of how many samples it has — accuracy alone can hide poor performance on small or hard classes.

Full per-class precision/recall/F1 and the confusion matrix are in [`docs/classification_report.csv`](./docs/classification_report.csv) and [`docs/confusion_matrix.png`](./docs/confusion_matrix.png).

**Weakest class**: `Corn___Cercospora_leaf_spot Gray_leaf_spot` (F1 = 0.784), which also has the fewest training samples of any class (86). The confusion matrix shows this class is confused mainly with other corn diseases (Common Rust, Northern Leaf Blight) — visually similar leaf-spot patterns — not with unrelated crops.

---

## Project structure

```
AGRISMART-AI/
├── app/
│   ├── backend/
│   │   └── main.py            # Flask API: /predict, /recommendation, /health
│   └── frontend/
│       ├── login.html          # Sign-up / login (Firebase Auth)
│       ├── index.html          # Main app: upload photo, view diagnosis
│       ├── styles.css          # Shared glassmorphism design system
│       └── firebase-config.js  # Firebase project config + shared helpers
├── model/
│   ├── train.py                # Two-stage training with early stopping
│   ├── preprocessing.py        # Dataset loading, train/eval transforms
│   ├── predict.py              # Inference + confidence thresholding
│   └── diagnose.py             # Debug tool: top-5 predictions for one image
├── modules/
│   ├── weather/weather.py      # Open-Meteo integration
│   ├── irrigation/irrigation.py# Rule-based irrigation logic
│   └── sustainability/sustainability.py  # Transparent scoring
├── scripts/
│   └── convert_checkpoint.py   # Converts a raw training checkpoint dict
│                                # into the state_dict + classes.json format
│                                # predict.py expects
├── experiments/
│   └── experiment_001/         # Trained weights, classes.json, metrics.json
├── demo_images/                # Anonymized sample images for judges
├── docs/                        # Confusion matrix, classification report
├── requirements.txt
└── run_agrismart.bat            # One-click launcher (Windows)
```

`data/train/` and `data/val/` are not committed (too large for Git) — see [Setup](#setup) for how to regenerate them.

---

## Setup

### 1. Clone and install dependencies

```powershell
git clone https://github.com/Jeelkumar03/AGRISMART-AI.git
cd AGRISMART-AI
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

> If PowerShell blocks the activation script, run this once:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Model weights

A trained checkpoint is already committed at `experiments/experiment_001/best_model.pth` — no training needed to run the app. To retrain from scratch, see [Training](#training).

### 3. Run it

**Option A — one click (Windows):**
```powershell
run_agrismart.bat
```
This starts the backend, the frontend server, and opens the browser automatically.

**Option B — manual (two terminals):**
```powershell
# Terminal 1
python app\backend\main.py

# Terminal 2
python -m http.server 8000 --directory app/frontend
```
Then open `http://localhost:8000`.

### 4. Firebase (only needed if you fork this project)

The repo already points at our Firebase project. If you're standing up your own:
1. Create a Firebase project → enable **Authentication → Email/Password**.
2. (Optional) Enable **Firestore** for storing user profiles — the app falls back to browser storage if this is off.
3. Replace the `firebaseConfig` object in `app/frontend/firebase-config.js` with your own project's values.

---

## API reference

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/predict` | POST | multipart form, field `image` | `{"disease": "...", "confidence": 0.94}` or `{"disease": "Uncertain", "confidence": 0.31, "raw_prediction": "..."}` |
| `/recommendation` | POST | JSON `{disease, lat, lon, soil_moisture}` | `{irrigation, weather, sustainability}` |
| `/health` | GET | — | `{"status": "ok"}` |

## Training

```powershell
python -m model.train --stage1-epochs 5 --stage2-epochs 30 --patience 5 --out_dir experiments/experiment_001
```
Requires `data/train/<class_name>/*.jpg` and `data/val/<class_name>/*.jpg` (an 80/20 split of the PlantVillage `color` folder). A GPU is strongly recommended — we trained on Kaggle's free tier.

---

## Known limitations

- **Domain gap**: the model is trained only on lab-condition PlantVillage images (plain background, single leaf, controlled lighting). Real-world photos — especially ones with natural backgrounds, poor lighting, or screen/web-compression artifacts — can produce a confident but incorrect prediction.
- **Corn disease confusion**: the three corn diseases (Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight) are visually similar and occasionally confused with each other; this is the model's main weak spot within the validation set itself.
- **Single-leaf classification, not detection**: the model classifies one leaf per photo. It does not locate or count multiple leaves/diseases in a single wide-angle image (that would require an object-detection architecture like YOLO, which is a different problem than the one this project solves).
- **Firestore is in test mode**: acceptable for a hackathon demo; production use would need proper security rules.

## Future work

- Fine-tune on field-condition datasets (e.g. PlantDoc) to close the domain gap.
- Aspect-ratio-preserving preprocessing instead of a direct square resize.
- Firestore security rules for production use.
- Optional cloud deployment for public access beyond local demo.

---

## Team

| Member | Role |
|---|---|
| Jeel | ML pipeline & backend |
| Prince | Evaluation, testing & report |
| Shivam | Backend & deployment |
| Shreya | Frontend |
| Shiya | Agri modules (weather, irrigation, sustainability) |
| Ronit | Docs, integration & demo |

Built for Smart India Hackathon.
