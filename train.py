"""
train.py
--------
1. Loads urls.csv (creates it first if it does not exist)
2. Converts every URL into numeric features
3. Splits data 80% train / 20% test
4. Trains Logistic Regression and Random Forest
5. Prints accuracy, precision, recall, F1 and the confusion matrix
6. Saves the best model (model.joblib) and two charts (PNG images)
"""

import os
import joblib
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # draw charts into files (no pop-up window needed)
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, ConfusionMatrixDisplay)

from features import FEATURE_NAMES, features_as_list

# ---------- Step 1: load the data ----------
if not os.path.exists("urls.csv"):
    print("urls.csv not found -> creating the sample dataset first...")
    import make_dataset
    make_dataset.main()

df = pd.read_csv("urls.csv")
print(f"Loaded {len(df)} URLs ({(df['label'] == 1).sum()} phishing, {(df['label'] == 0).sum()} legitimate)\n")

# ---------- Step 2: turn URLs into numbers ----------
X = pd.DataFrame([features_as_list(u) for u in df["url"]], columns=FEATURE_NAMES)
y = df["label"]

# ---------- Step 3: 80/20 split ----------
# stratify=y keeps the phishing/legitimate ratio the same in both parts
# random_state makes the split repeatable
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y)
print(f"Training rows: {len(X_train)}, Testing rows: {len(X_test)}\n")

# ---------- Step 4: define the two models ----------
# Logistic Regression works best when numbers are on a similar scale,
# so we put a StandardScaler in front of it.
models = {
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
}

# ---------- Step 5: train and evaluate ----------
results = {}
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

for ax, (name, model) in zip(axes, models.items()):
    model.fit(X_train, y_train)          # learn from training data
    y_pred = model.predict(X_test)       # predict on data the model has never seen

    results[name] = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1-score": f1_score(y_test, y_pred),
    }
    cm = confusion_matrix(y_test, y_pred)

    print(f"=== {name} ===")
    for metric, value in results[name].items():
        print(f"  {metric:10s}: {value:.3f}")
    print("  Confusion matrix (rows = actual, columns = predicted):")
    print(f"                 Legit  Phishing")
    print(f"    Legit        {cm[0][0]:5d}  {cm[0][1]:8d}")
    print(f"    Phishing     {cm[1][0]:5d}  {cm[1][1]:8d}\n")

    ConfusionMatrixDisplay(cm, display_labels=["Legit", "Phishing"]).plot(ax=ax, colorbar=False)
    ax.set_title(name)

plt.tight_layout()
plt.savefig("confusion_matrices.png", dpi=120)
plt.close()

# ---------- Step 6: pick and save the best model (by F1-score) ----------
best_name = max(results, key=lambda n: results[n]["F1-score"])
joblib.dump(models[best_name], "model.joblib")
print(f"Best model: {best_name} (F1 = {results[best_name]['F1-score']:.3f}) -> saved as model.joblib")

# ---------- Step 7: Random Forest feature importance chart ----------
rf = models["Random Forest"]
importance = pd.Series(rf.feature_importances_, index=FEATURE_NAMES).sort_values()

plt.figure(figsize=(8, 5))
importance.plot(kind="barh", color="#3b6fd4")
plt.title("Random Forest - Feature Importance")
plt.xlabel("Importance (higher = more useful for the decision)")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=120)
plt.close()

print("\nFeature importance (Random Forest):")
for feat, val in importance.sort_values(ascending=False).items():
    print(f"  {feat:22s} {val:.3f}")
print("\nSaved charts: confusion_matrices.png, feature_importance.png")
