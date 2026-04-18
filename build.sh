#!/bin/bash
echo "Downloading dataset..."
pip install -r requirements.txt

# Download EMSCAD dataset
python -c "
import urllib.request
import os

url = 'https://raw.githubusercontent.com/YOUR_USERNAME/fake-job-detector/main/fake_job_postings.csv'
if not os.path.exists('fake_job_postings.csv'):
    print('Downloading fake_job_postings.csv...')
    urllib.request.urlretrieve(url, 'fake_job_postings.csv')
    print('Done!')
else:
    print('Dataset already exists')
"

echo "Training model..."
python train_model.py
echo "Build complete!"