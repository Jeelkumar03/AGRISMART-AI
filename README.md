# AgriSmart AI

**Crop disease detection from a single leaf photo — with weather, irrigation, sustainability, and AI-generated advice in your own language.**

Built by **Team Curious Coders** for Smart India Hackathon (SIH).

A farmer logs in, uploads a photo of a leaf, and within seconds gets: the disease (or confirmation the plant is healthy), today's weather risk, whether to irrigate, a sustainability score, and a plain-language explanation with concrete next steps — all in the language they picked at login.

---

## Try it yourself

Five sample leaf photos are in [`demo_images/`](./demo_images) — pulled from our validation set (images the model never saw during training) and renamed so the disease name isn't given away. Upload `test1` through `test5` and see what the model predicts. Once you've tried all five, open [`demo_images/answer_key.txt`](./demo_images/answer_key.txt) to check against the ground truth.

You're also welcome to test with your own photos. For the most reliable results:
- Use a plain-background, close-up photo of a single leaf — a reference-style photo works better than one of a leaf still on the plant in a field.
- Crop the image to a roughly square (1:1) frame before uploading.
- Avoid blurry, low-resolution, or re-photographed/screenshotted images.

The model is trained on the PlantVillage dataset, which consists of controlled, lab-condition photos. Images that match that style get the most accurate results — see [Known Limitations](#known-limitations).

---

## What it does

| Feature | Description |
|---|---|
| **Accounts** | Email/password sign-up and login (Firebase Auth). Sign-up captures name, email, password, and location — used for weather lookups. |
| **Disease diagnosis** | Upload a leaf photo, get the disease name and a confidence score. Below 50% confidence, the app says so honestly instead of guessing. |
| **Weather risk** | Live temperature, humidity, and rain probability for the user's location, with advisory notes (e.g. "high humidity increases fungal disease risk"). |
| **Irrigation guidance** | A simple, explainable rule combining soil moisture and rain forecast — irrigate now, or wait. |
| **Sustainability score** | A transparent 0–100 score built from crop health, water efficiency, and resource usage, with the exact weighting shown — not a black box. |
| **AI explanation & advice** | A Gemini-powered summary that explains the result in plain language and lists 2–3 concrete next steps — grounded strictly in the numbers already computed by the backend (see [Generative AI](#generative-ai-explanation--advice)). |
| **Multi-language UI** | The whole app — auth, navigation, and the AI-generated explanation/advice — is available in English, Hindi, Gujarati, Marathi, Tamil, and Telugu, switchable from a selector in the top-right corner on every page. |

---

## How it works

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

- **Model**: MobileNetV3-Large, transfer-learned from ImageNet weights on the [PlantVillage dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset) (`color` subset, 38 classes across 14 crops).
- **Training**: two-stage — frozen backbone first (fast head-only warm-up), then full fine-tuning at a lower learning rate, with early stopping on validation macro-F1 and class-weighted loss to compensate for underrepresented classes. Trained on Kaggle's free T4×2 GPU.
- **Backend**: Flask, five endpoints (below).
- **Frontend**: vanilla HTML/CSS/JS, no build step — a glassmorphism UI with Firebase email/password authentication and client-side i18n.

---

## Generative AI: explanation & advice

The `/explain` endpoint calls Gemini (`gemini-2.5-flash`, free tier) with a prompt that hands it the diagnosis, irrigation decision, weather figures, and sustainability score already computed by the rest of the backend, and explicitly instructs it to **use only those facts** — no new diagnoses, numbers, or treatment specifics may be invented. This is a deliberate grounding pattern: the model interprets and explains data it's given, in the farmer's selected language, rather than answering free-form and risking hallucinated advice. It returns:
- A 3–4 sentence plain-language explanation
- 2–3 concrete, non-prescriptive next steps (no specific pesticide brands or dosages)

If the API key is missing or the service is unreachable, these two cards simply don't render — the rest of the app (diagnosis, weather, irrigation, sustainability) is unaffected.

---

## Language support

Six languages are supported: English, Hindi (हिंदी), Gujarati (ગુજરાતી), Marathi (मराठी), Tamil (தமிழ்), and Telugu (తెలుగు). The selector appears top-right on both the login page and the main app; the choice persists across both via `localStorage`.

- **Static UI** (buttons, labels, headings, error messages) is translated instantly via a client-side dictionary (`app/frontend/i18n.js`).
- **The AI explanation and advice** are generated directly in the selected language by Gemini — not machine-translated after the fact.
- **Known scope limit**: the raw irrigation "reason" and weather "advice" strings returned by the backend are still English-only (they're plain Python strings, not templated). The same information reaches the farmer in their language via the AI explanation card regardless.

---

## Model performance

| Metric | Value |
|---|---|
| Validation accuracy | 97.2% |
| Validation macro-F1 | 0.9618 |
| Best epoch | 24 |
| Classes | 38 (14 crops) |
| Validation set size | 10,861 images |

Macro-F1 (not accuracy) is the primary metric, because it weighs every class equally regardless of sample count — accuracy alone can hide poor performance on small or hard classes.

Full per-class precision/recall/F1 and the confusion matrix are in [`docs/classification_report.csv`](./docs/classification_report.csv) and [`docs/confusion_matrix.png`](./docs/confusion_matrix.png).

**Weakest class**: `Corn___Cercospora_leaf_spot Gray_leaf_spot` (F1 = 0.784), which also has the fewest training samples of any class (86). The confusion matrix shows this class is confused mainly with other corn diseases (Common Rust, Northern Leaf Blight) — visually similar leaf-spot patterns — not with unrelated crops.

---

## Project structure

```
AGRISMART-AI/
├── app/
│   ├── backend/
│   │   └── main.py            # Flask API: /predict, /recommendation, /explain, /health
│   └── frontend/
│       ├── login.html          # Sign-up / login (Firebase Auth) + language switcher
│       ├── index.html          # Main app: upload, diagnosis, AI advice + language switcher
│       ├── styles.css          # Shared glassmorphism design system
│       ├── firebase-config.js  # Firebase project config + shared helpers
│       └── i18n.js             # Client-side translation dictionary (6 languages)
├── model/
│   ├── train.py                # Two-stage training, early stopping, class-weighted loss
│   ├── preprocessing.py        # Dataset loading, train/eval transforms
│   ├── predict.py              # Inference + confidence thresholding
│   └── diagnose.py             # Debug tool: top-5 predictions for one image
├── modules/
│   ├── weather/weather.py      # Open-Meteo integration
│   ├── irrigation/irrigation.py# Rule-based irrigation logic
│   ├── sustainability/sustainability.py  # Transparent scoring
│   └── explain/explain.py      # Grounded GenAI explanation + advice (Gemini)
├── scripts/
│   └── convert_checkpoint.py   # Converts a raw training checkpoint dict into the
│                                # state_dict + classes.json format predict.py expects
├── experiments/
│   └── experiment_001/         # Trained weights, classes.json, metrics.json
├── demo_images/                # Anonymized sample images for judges
├── docs/                        # Confusion matrix, classification report
├── requirements.txt
├── run_agrismart.bat            # One-click launcher (Windows)
├── .env.example                 # Template for the Gemini API key
└── .gitignore
```

`data/train/` and `data/val/` are not committed (too large for Git) — see [Setup](#setup) for how to regenerate them. `.env` (your real API key) is also never committed.

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

### 3. Gemini API key (for the AI explanation feature)

1. Get a free key at [aistudio.google.com](https://aistudio.google.com) (no credit card required).
2. Copy `.env.example` to `.env` in the repo root and paste your key:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   `.env` is gitignored — never commit it. Without this key, the app still works; the "In plain words" and "What to do" cards just won't appear.

### 4. Run it

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
Then open `http://localhost:8000` (it redirects to the login page if you're not signed in).

### 5. Firebase (only needed if you fork this project)

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
| `/explain` | POST | JSON `{crop, condition, confidence, irrigation, weather, sustainability, language}` | `{"explanation": "...", "next_steps": ["...", "..."]}` |
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
- **Single-leaf classification, not detection**: the model classifies one leaf per photo. It does not locate or count multiple leaves/diseases in a single wide-angle image (that would require an object-detection architecture like YOLO, a different problem than the one this project solves).
- **Partial localization**: raw irrigation/weather text from the backend is English-only; the AI explanation card covers the gap by summarizing the same information in the selected language.
- **Firestore is in test mode**: acceptable for a hackathon demo; production use would need proper security rules.

## Future work

- Fine-tune on field-condition datasets (e.g. PlantDoc) to close the domain gap.
- Template the irrigation/weather strings so the raw cards are fully localized, not just the AI summary.
- Firestore security rules for production use.
- Optional cloud deployment for public access beyond local/LAN demo.

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
