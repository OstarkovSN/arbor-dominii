import os
from app.common.preprocess import preprocess_default

preprocess_default()

os.makedirs('app/data/final', exist_ok=True)

with open('app/data/final/results.tsv', 'w', encoding='utf-8') as f:
    f.write('test')