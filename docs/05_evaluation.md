# Evaluation

## Metrics and rationale
- Binary classification metrics are computed: F1, precision, recall, accuracy, ROC-AUC, PR-AUC.
- Training script logs metrics and confusion matrix/classification report to MLflow.

Evidence
```text
# src/models/train_model.py
metrics = {
    "f1_score": f1_score(y_test, y_pred),
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred),
    "recall": recall_score(y_test, y_pred),
    "roc_auc": roc_auc_score(y_test, y_pred_proba),
    "pr_auc": pr_auc,
}
mlflow.log_metrics(metrics)
mlflow.log_text(str(cm), "confusion_matrix.txt")
mlflow.log_text(report, "classification_report.txt")
```
```text
# src/models/predict_model.py
f1 = f1_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)
```

## Model selection criteria
- New model is promoted to Production if its F1 score exceeds the current production model's F1.

Evidence
```text
# src/models/train_model.py
new_f1 = metrics["f1_score"]
is_better = new_f1 > current_f1
if is_better:
    client.transition_model_version_stage(
        MODEL_NAME, model_details.version, "Production"
    )
```

## Thresholds
Status: Not present in repo
- No explicit classification thresholds or business KPIs are documented beyond default XGBoost predictions.

Expected in mature setup
- A target F1/precision/recall threshold per deployment environment and a documented decision threshold.

Actionable recommendations
- Add a threshold config in `params.yaml` and log it to MLflow.
- Track calibration metrics (Brier score) and add a threshold selection report to `reports/`.

## Error analysis
Status: Not present in repo
- No dedicated error analysis notebook/report is included; only confusion matrix and classification report logs exist.

Expected in mature setup
- Class-wise error analysis with segment breakdowns (by Location, Season, Year) and drift-aware slices.

Actionable recommendations
- Add an `analysis/error_analysis.py` that logs per-segment metrics to MLflow.
- Persist top false positives/negatives to `reports/` for review.
