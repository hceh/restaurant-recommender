"""
Data is downloaded and unzipped from https://www.yelp.com/dataset
The json files are not suitable to read straight into pandas (not comma seperated or in list), so the following code must be used
Adjust initial dataset path as necessary
"""

from pathlib import Path

import pandas as pd

dataset_path = Path.home() / 'Downloads/yelp_dataset/'
download_path = dataset_path / 'yelp_academic_dataset_business.json'
converted_path = Path('../../data/yelp_academic_dataset_business.json')

with open(download_path, 'r') as f:  # ignore warning, open works with pathlib but isn't in hinting
    json_lines = f.readlines()

json_lines = [_.replace('\n', ',\n') for _ in json_lines]
json_lines[0] = '[' + json_lines[0]
json_lines[-1] = json_lines[-1] + ']'

converted_path.parent.mkdir(exist_ok=True)

with open(converted_path, 'w') as f:
    f.writelines(json_lines)

# test dataset
try:
    df = pd.read_json(converted_path, orient='records')
    print('Conversion successful')
except ValueError:
    print('Conversion failed')
