"""
app.py
------
A tiny Flask web app. The user pastes a URL, we extract the same features
used in training, ask the saved model for a prediction, and show the result.
Run with:  python app.py   then open http://127.0.0.1:5000
"""

import os
import sys
import joblib
import pandas as pd
from flask import Flask, render_template, request

from features import FEATURE_NAMES, extract_features

app = Flask(__name__)

# Load the trained model once when the app starts (not on every request)
if not os.path.exists("model.joblib"):
    sys.exit("model.joblib not found. Run 'python train.py' first.")
model = joblib.load("model.joblib")


@app.route("/", methods=["GET", "POST"])
def index():
    result = None   # will hold the prediction to show on the page
    error = None
    url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url:
            error = "Please paste a URL first."
        else:
            try:
                # 1. URL -> features (same function used in training)
                feats = extract_features(url)
                # Keep the same column order and names as in training
                row = pd.DataFrame([[feats[n] for n in FEATURE_NAMES]], columns=FEATURE_NAMES)

                # 2. Model gives the probability of each class: [legit, phishing]
                prob_legit, prob_phish = model.predict_proba(row)[0]

                # 3. Pick the more likely class and show its probability as confidence
                is_phishing = prob_phish >= 0.5
                result = {
                    "label": "Not Safe - Likely Phishing" if is_phishing else "Looks Safe",
                    "is_phishing": is_phishing,
                    "confidence": round((prob_phish if is_phishing else prob_legit) * 100, 1),
                    "features": feats,
                }
            except Exception:
                error = "Could not analyse that URL. Please check it and try again."

    return render_template("index.html", url=url, result=result, error=error)


if __name__ == "__main__":
    # Hosting services give the port through the PORT environment variable.
    # Locally it falls back to 5000. Debug mode is OFF unless FLASK_DEBUG=1.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
