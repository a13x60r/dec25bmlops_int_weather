"""
Load processed data into MongoDB to build a noSQL database.

This script loads the preprocessed train/test data into MongoDBfor use in model training.

Input:  data/processed/X_train.csv, X_test.csv, y_train.csv, y_test.csv
Output: MongoDB database

Usage:
    python src/data/load_to_db
"""

import pandas as pd
from pymongo import MongoClient
import sys
from pathlib import Path


# Add project root to path, MongoDB connection parameters from params.yaml
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import PARAMS, MONGO_URI
DB_NAME = PARAMS['database']['db_name']
COLLECTION_NAME = PARAMS['database']['collection']


# ==================== Step 1 ====================
# Load processed data
X_train = pd.read_csv('data/processed/X_train.csv')
X_test = pd.read_csv('data/processed/X_test.csv')
y_train = pd.read_csv('data/processed/y_train.csv')
y_test = pd.read_csv('data/processed/y_test.csv')

print('Step 1: Processed data loaded.')


# ==================== Step 2 ====================
# Combine data

# Combine X and y for train
train_data = pd.concat([X_train, y_train], axis=1)
train_data['split'] = 'train'

# Combine X and y for test
test_data = pd.concat([X_test, y_test], axis=1)
test_data['split'] = 'test'

# Combine train and test
df_combined = pd.concat([train_data, test_data], axis=0, ignore_index=True)

print('Step 2: Combine data.')


# ==================== Step 3 ====================
# Connect to MongoDB

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f'Step 3: Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}')
except Exception as e:
    print(f'ERROR: Could not connect to MongoDB!')
    print(f'Error: {e}')
    print('Make sure MongoDB is running: docker-compose up -d mongodb')
    exit(1)


# ==================== Step 4 ====================
# Delete old data from MongoDB

result = collection.delete_many({})
print(f'Step 4: Deleted {result.deleted_count} old records.')


# ==================== Step 5 ====================
# Insert data

records = df_combined.to_dict('records')
collection.insert_many(records)

print(f'Step 5: Inserted {len(records):,} records into MongoDB.')


# ==================== Step 6  ====================
# Data verification

total_count = collection.count_documents({})
train_count = collection.count_documents({'split': 'train'})
test_count = collection.count_documents({'split': 'test'})

print(f'Total documents in MongoDB: {total_count:,}')
print(f'Train documents: {train_count:,}')
print(f'Test documents: {test_count:,}')

# Show sample record
sample = collection.find_one({}, {'_id': 0})
if sample:
    print(f'\nSample record columns: {list(sample.keys())[:10]}...')
    print(f'Total columns: {len(sample.keys())}')


client.close()

print('Data loaded to MongoDB.')
print('Next step model training: python src/models/train_model.py')


