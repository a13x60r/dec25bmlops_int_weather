"""
Train XGBoost model for rain prediction in Australia.
XGBoost was found as the best suited model for this binary classification task using LazyCLassifier on the cleaned dataset.
XGBoost parameters were identified using GridSearch.

This script loads processed data, applies SMOTE on training data for class balancing, trains an XGBoost classifier  and saves the trained model.

Input:  data/procesed/X_train, y_train
Output: models/xgboost_model.pkl

Usage:
    python src/models/train_model.py
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import pickle
import sys
from pathlib import Path


# Import params from params.yaml
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import PARAMS, MONGO_URI


# ==================== Step 1 ====================
# Load train data
X_train = pd.read_csv('data/processed/X_train.csv')
y_train = pd.read_csv('data/processed/y_train.csv')

print('Step 1: Training data loaded')
print(f'X_train: {X_train.shape}')
print(f'y_train: {y_train.shape}')


# ==================== Step 2 ====================
# Apply SMOTE for class balancing on train data

print('Step 2: SMOTE on training data to balance class distribution')
print(f'Before SMOTE:')
print(y_train.value_counts())

smote = SMOTE(random_state=PARAMS['data']['random_state'])
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

print(f'After SMOTE:')
print(y_train_smote.value_counts())


# ==================== Step 3 ====================
# Train XGBoost model

# Get model parameters from params.yaml
model_params = {
    'max_depth': PARAMS['model']['max_depth'],
    'learning_rate': PARAMS['model']['learning_rate'],
    'n_estimators': PARAMS['model']['n_estimators'],
    'colsample_bytree': PARAMS['model']['colsample_bytree'],
    'subsample': PARAMS['model']['subsample'],
    'gamma': PARAMS['model']['gamma'],
    'min_child_weight': PARAMS['model']['min_child_weight'],
    'random_state': PARAMS['model']['random_state'],
    'eval_metric': 'logloss',
    'use_label_encoder': False
}

print('Step 3: Model training')
print(f'Model parameters for XGBoost: {model_params}')

# Train model
model = xgb.XGBClassifier(**model_params)
model.fit(X_train_smote, y_train_smote)

print('XGBoost model trained.')


# ==================== Step 4 ====================
# Save model

models_dir = Path('models')
models_dir.mkdir(exist_ok=True)

model_path = models_dir / 'xgboost_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f'Step 4: Model saved {model_path}')

