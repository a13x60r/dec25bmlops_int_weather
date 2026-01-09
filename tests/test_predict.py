# Test API prediction

import pandas as pd
import requests

# Load one sample from test data
X_test = pd.read_csv('data/processed/X_test.csv')
sample = X_test.iloc[0].to_dict()

# Make prediction request
response = requests.post('http://localhost:8000/predict', json=sample)

# Print result
print(response.json())
