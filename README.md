# Fake Job Detector India

ML-powered fake job post detector trained on 96,000+ real Indian and global job postings.

## What it does
- Detects fake/scam job posts with 99.67% accuracy
- Works on Naukri, LinkedIn, Indeed via Chrome Extension
- India-specific scam pattern detection
- Shows risk score, verdict, and red flags

## Tech stack
- Python · Flask · scikit-learn · Random Forest · TF-IDF
- Chrome Extension (Manifest V3)
- Trained on EMSCAD + Naukri India datasets

## How to run locally
```bash
pip install -r requirements.txt
python train_model.py
python app.py
```
Open https://fake-job-detector-np6q.onrender.com

## Chrome Extension
Load the `extension/` folder in Chrome developer mode.

## Accuracy
- Random Forest: 99.67% accuracy · F1: 0.7789
- Trained on 96,674 job posts
<<<<<<< HEAD
- India + Global coverage
=======
- India + Global coverage
>>>>>>> dba8d61266275ec1a06a924ad02a64d3d939d5fd
