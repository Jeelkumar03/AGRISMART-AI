# AgriSmart AI

**Crop disease detection from a single leaf photo — with weather, irrigation, sustainability, and AI-generated advice in the farmer's own language.**

Built by **Team Curious Coders** for Smart India Hackathon (SIH). A farmer uploads a leaf photo and gets, in seconds: the disease (or confirmation the plant is healthy), today's weather risk, an irrigation call, a sustainability score, and a plain-language explanation with next steps — in one of six languages.

---

## Setup — reproduce a prediction in under 10 minutes

**Fastest path (verifies the core ML task, ~2 minutes, no browser needed):**

```powershell
git clone https://github.com/Jeelkumar03/AGRISMART-AI.git
cd AGRISMART-AI
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python model\predict.py --image demo_images\test1.jpg
```
Prints the predicted class and confidence directly. The trained checkpoint (`experiments/experiment_001/best_model.pth`) is already committed — no training required. Try any of `demo_images/test1.jpg` through `test5.jpg`; the ground truth for each is in [`demo_images/answer_key.txt`](./demo_images/answer_key.txt).

> If PowerShell blocks the venv activation script:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Full experience (web app with weather/irrigation/sustainability/AI advice, ~5 more minutes):**

```powershell
run_agrismart.bat
```
This starts the backend, the frontend server, and opens the browser automatically (`http://localhost:8000`). Firebase auth is already configured — create an account with any email/password to sign in. Upload a demo image and get the full report.

**Optional — AI explanation & advice cards:** these need a free Gemini key (no credit card). Get one at [aistudio.google.com](https://aistudio.google.com), copy `.env.example` to `.env`, and paste it in as `GEMINI_API_KEY=...`. Without it, the app still works — those two cards just won't render.

---

## Core + bonus modules

| | Module | What it does |
|---|---|---|
| **Core** | Disease classification (CV) | MobileNetV3-Large, transfer-learned on PlantVillage, 38 classes. `predict(image_path) → class_label` via `model/predict.py`. |
| Bonus | Weather risk | Live temperature/humidity/rain forecast via Open-Meteo, with advisory notes. |
| Bonus | Irrigation guidance | Deterministic, explainable rule (soil moisture + rain forecast) — irrigate or wait. |
| Bonus | Sustainability score | Transparent 0–100 score with a documented weighting formula — not a black box. |
| Bonus | Generative AI explanation & advice | Gemini-generated plain-language summary + concrete next steps, grounded strictly in the numbers the backend already computed. |
| Bonus | Multi-language UI | English, Hindi, Gujarati, Marathi, Tamil, Telugu — switchable app-wide, including the AI-generated text. |
| Bonus | Accounts | Email/password auth (Firebase), captures location for weather lookups. |

---

## Try it yourself

Five sample leaf photos are in [`demo_images/`](./demo_images) — from our validation set, renamed so the disease isn't given away. Upload `test1` through `test5` and compare against [`demo_images/answer_key.txt`](./demo_images/answer_key.txt).

Testing with your own photo? For reliable results: a plain-background, close-up, roughly square (1:1) photo of a single leaf, not a re-photographed screenshot. See [Known Limitations](#known-limitations) for why this matters.

---

## Dataset

**Source**: [PlantVillage](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset) (`color` subset) — 54,305 lab-condition leaf images across 38 crop-disease classes (14 crops), originally from Hughes & Salathé's open-access plant health image repository (2015). We split it 80/20 into train/val ourselves (`data/train/`, `data/val/`; not committed — regenerate via `split_dataset.py` or the Kaggle notebook workflow described in [Training](#training)).

**License**: distributed openly for research use; check the exact license tag on the Kaggle listing linked above before any commercial use. Not modified beyond our own train/val split.

---

## Model performance

| Metric | Value |
|---|---|
| Validation accuracy | 97.2% |
| Validation macro-F1 | 0.9618 |
| Best epoch | 24 |
| Classes | 38 (14 crops) |
| Validation set size | 10,861 images |

Macro-F1 (not accuracy) is our primary metric — it weighs every class equally regardless of sample count, so it doesn't hide poor performance on small or hard classes.

Full per-class precision/recall/F1 and the confusion matrix: [`docs/classification_report.csv`](./docs/classification_report.csv), [`docs/confusion_matrix.png`](./docs/confusion_matrix.png).

**Weakest class**: `Corn___Cercospora_leaf_spot Gray_leaf_spot` (F1 = 0.784) — also the class with the fewest training samples (86). Confused mainly with other corn diseases (Common Rust, Northern Leaf Blight), not unrelated crops.

---

## Architecture overview

```
┌──────────┐  login/signup  ┌────────────┐
│  Browser  │ ──────────────▶│  Firebase   │
│           │◀────────────── │  Auth       │
└────┬─────┘                └────────────┘
     │ photo
     ▼
┌─────────────┐   disease    ┌──────────────┐
│  Flask       │◀────────────│ MobileNetV3-L │
│  /predict    │─────────────▶│  classifier   │
└──────┬──────┘  diagnosis   └──────────────┘
       │ disease name
       ▼
┌────────────────┐   weather+irrigation+sustainability   ┌───────────────┐
│ /recommendation │──────────────────────────────────────▶│ Open-Meteo API │
└──────┬─────────┘                                        └───────────────┘
       │ all computed facts + selected language
       ▼
┌─────────────┐
│  /explain    │──▶ Gemini API (grounded prompt: "use only these facts")
└─────────────┘
```

- **Model**: MobileNetV3-Large (ImageNet-pretrained), two-stage transfer learning — frozen-backbone warm-up, then full fine-tuning at a lower learning rate, with early stopping on validation macro-F1 and class-weighted loss to compensate for underrepresented classes. Trained on Kaggle's free T4×2 GPU.
- **Backend**: Flask, five endpoints (see [API reference](#api-reference)).
- **Frontend**: vanilla HTML/CSS/JS, no build step — glassmorphism UI, Firebase auth, client-side i18n.

## Generative AI: explanation & advice

`/explain` calls Gemini (`gemini-2.5-flash`, free tier) with the diagnosis, irrigation decision, weather figures, and sustainability score already computed by the rest of the backend, explicitly instructed to **use only those facts** — no new diagnoses, numbers, or treatment specifics invented. The model interprets and explains data it's given, in the farmer's selected language, rather than answering free-form. Returns a 3–4 sentence explanation and 2–3 non-prescriptive next steps (no pesticide brands/dosages). If the API key is missing, these two cards simply don't render — the rest of the app is unaffected.

## Language support

Six languages: English, Hindi (हिंदी), Gujarati (ગુજરાતી), Marathi (मराठी), Tamil (தமிழ்), Telugu (తెలుగు). Selector top-right on every page; choice persists via `localStorage`. Static UI translates instantly via a client-side dictionary (`app/frontend/i18n.js`); the AI explanation/advice are generated directly in the selected language by Gemini, not machine-translated after the fact. Known gap: the raw irrigation/weather strings from the backend are still English-only — the AI explanation card covers the same information in the selected language regardless.

---

## Known limitations

- **Domain gap**: trained only on lab-condition PlantVillage images (plain background, single leaf, controlled lighting). Real-world photos — natural backgrounds, poor lighting, or re-photographed/screen-compression artifacts — can produce a confident but incorrect prediction. This is the primary axis we'd target next (see Future work).
- **Corn disease confusion**: the three corn diseases (Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight) are visually similar and occasionally confused with each other — the model's main weak spot even within the validation set.
- **Single-leaf classification, not detection**: classifies one leaf per photo; doesn't locate/count multiple leaves in a wide-angle image (a different problem, suited to detection architectures like YOLO, not what this project targets).
- **Partial localization**: raw irrigation/weather backend strings are English-only; the AI explanation card covers this in-language.
- **Firestore in test mode**: fine for a hackathon demo; production would need proper security rules.

## Future work

- Fine-tune on field-condition data (e.g. PlantDoc, which shares ~24 classes with our taxonomy) to directly close the domain gap — scoped but not yet executed.
- Template the irrigation/weather strings for full localization, not just the AI summary.
- Firestore security rules for production use.
- Optional cloud deployment for public access beyond local/LAN demo.

---

## API reference

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/predict` | POST | multipart form, field `image` | `{"disease": "...", "confidence": 0.94}` or `{"disease": "Uncertain", "confidence": 0.31, "raw_prediction": "..."}` |
| `/recommendation` | POST | JSON `{disease, lat, lon, soil_moisture}` | `{irrigation, weather, sustainability}` |
| `/explain` | POST | JSON `{crop, condition, confidence, irrigation, weather, sustainability, language}` | `{"explanation": "...", "next_steps": [...]}` |
| `/health` | GET | — | `{"status": "ok"}` |

CLI equivalent of `/predict`: `python model/predict.py --image <path>` — loads the trained checkpoint and prints the predicted class + confidence, no manual steps.

## Training

```powershell
python -m model.train --stage1-epochs 5 --stage2-epochs 30 --patience 5 --out_dir experiments/experiment_001
```
Requires `data/train/<class_name>/*.jpg` and `data/val/<class_name>/*.jpg` (an 80/20 split of PlantVillage's `color` folder). A GPU is strongly recommended — we trained on Kaggle's free tier.

---

## Project structure

```
AGRISMART-AI/
├── app/
│   ├── backend/main.py         # Flask API: /predict, /recommendation, /explain, /health
│   └── frontend/
│       ├── login.html           # Sign-up / login + language switcher + animated logo
│       ├── index.html           # Main app: upload, diagnosis, AI advice
│       ├── styles.css           # Shared glassmorphism design system
│       ├── firebase-config.js   # Firebase config + shared helpers
│       └── i18n.js              # Translation dictionary (6 languages)
├── model/
│   ├── train.py                 # Two-stage training, early stopping, class-weighted loss
│   ├── preprocessing.py         # Dataset loading, train/eval transforms
│   ├── predict.py               # Inference + confidence thresholding (CLI + function)
│   └── diagnose.py              # Debug tool: top-5 predictions for one image
├── modules/
│   ├── weather/weather.py
│   ├── irrigation/irrigation.py
│   ├── sustainability/sustainability.py
│   └── explain/explain.py       # Grounded GenAI explanation + advice (Gemini)
├── scripts/convert_checkpoint.py
├── experiments/experiment_001/  # Trained weights, classes.json, metrics.json
├── demo_images/                 # Anonymized sample images for judges
├── docs/                         # Confusion matrix, classification report
├── requirements.txt
├── run_agrismart.bat
├── .env.example
└── .gitignore
```

---

## Demo video & deployment

- **Demo video**: [Watch on YouTube](https://youtu.be/oKUSdgMYjSo)
- **Deployed app**: not hosted — this is a local/LAN demo by design (see submission notes). Run via [Setup](#setup--reproduce-a-prediction-in-under-10-minutes) above.

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
