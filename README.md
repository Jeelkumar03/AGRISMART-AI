# AgriSmart AI

Crop-disease detection from leaf photos, plus weather, irrigation, and sustainability recommendations.

## What's in here

```
model/        training, evaluation, and prediction code (the mandatory core)
app/backend/  Flask API wrapping the model and bonus modules
app/frontend/ simple upload UI
modules/      weather, irrigation, sustainability logic
experiments/  saved model weights + metrics per training run
report/       final one-page model report
tests/        edge-case tests
```

## Setup (~10 minutes)

```bash
git clone <this-repo-url>
cd AgriSmart-AI
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Get the dataset

Download the organizers' dataset and arrange it like this:

```
data/train/<class_name>/*.jpg
data/val/<class_name>/*.jpg
```

Sanity check everything is wired up correctly:

```bash
python model/test_setup.py
```

Inspect class counts (imbalance matters -- see macro-F1 below):

```bash
python model/preprocessing.py
```

## Train

```bash
python model/train.py --epochs 10 --lr 1e-4
```

Saves the best checkpoint (by validation macro-F1) to `experiments/experiment_001/best_model.pth`.

## Evaluate

```bash
python model/evaluate.py --model experiments/experiment_001/best_model.pth
```

Prints accuracy, macro-F1, precision, recall, and per-class report; saves a confusion matrix PNG.

## Predict a single image

```bash
python model/predict.py --image sample.jpg
```

## Run the full app

```bash
# terminal 1
python app/backend/main.py

# terminal 2 -- just open this file in a browser
open app/frontend/index.html
```

## Metrics explained

- **Accuracy** -- % of correct guesses overall. Misleading with class imbalance.
- **Macro-F1** -- averages the F1 score across classes equally, so rare diseases count as much as common ones. This is the primary competition metric.
- **Confusion matrix** -- shows which classes get mixed up with which.

## Known limitations

- Training data is lab-condition images; real field photos (different lighting, background clutter) are harder. Augmentation in `preprocessing.py` helps but doesn't fully close the gap.
- Predictions below 50% confidence are returned as "Uncertain" rather than a forced guess (`CONFIDENCE_THRESHOLD` in `predict.py`).
- Sustainability scoring uses a placeholder `resource_usage` value -- replace with real data (pesticide logs, etc.) when available.
