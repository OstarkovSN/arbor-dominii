import os
import json
from app.common.preprocess import preprocess_default


#CONFIG = json.load(open('config.json'))


preprocess_default()

with open('environment/results.tsv', 'w', encoding='utf-8') as f:
    f.write('test')

