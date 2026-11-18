# AI-Based Phishing Detection System (Mini Project)

Classifies a URL as **Phishing** or **Legitimate** using machine learning and shows the result on a simple web page.
It only looks at the text of the URL (no internet calls), so it is fast and easy to understand.

## Files

| File | Purpose |
|------|---------|
| `features.py` | Converts a URL into 10 numbers (features) |
| `make_dataset.py` | Creates a sample dataset `urls.csv` (~1000 URLs). Only needed if you have no real dataset |
| `train.py` | Trains Logistic Regression and Random Forest, prints metrics, saves the best model and charts |
| `app.py` | Flask web app |
| `templates/index.html` | The web page |
| `requirements.txt` | Python libraries needed |

## Setup and run (macOS / Linux)

```bash
cd phishing-detector
python3 -m venv venv              # optional but recommended
source venv/bin/activate
pip install -r requirements.txt
python train.py                   # trains the models, creates model.joblib + 2 PNG charts
python app.py                     # then open http://127.0.0.1:5000
```

On Windows: use `python` instead of `python3`, and `venv\Scripts\activate` instead of `source venv/bin/activate`.

## How it works

1. **Features** - each URL becomes 10 numbers: length, dots, hyphens, digits, has `@`, has IP address, uses HTTPS, number of subdomains, count of suspicious words (login, verify, secure, update, bank, account), uses a URL shortener.
2. **Training** - 80% of the URLs are used to train, 20% are kept hidden to test.
3. **Two models are compared** - Logistic Regression (simple, draws a straight-line boundary) and Random Forest (many decision trees voting). The one with the better F1-score is saved.
4. **Web app** - loads the saved model, converts the pasted URL to the same 10 features, and shows the predicted class with the model's probability as "confidence".

## Using a real dataset

`urls.csv` is generated from rules, so the scores on it are optimistic. For a more honest result, replace `urls.csv` with a real dataset that has two columns, `url` and `label` (0 = legitimate, 1 = phishing), then run `python train.py` again. Public URL datasets exist on Kaggle (search "phishing URL dataset"). Note that the UCI "Phishing Websites" dataset contains pre-computed features, not URLs, so it would need a different `train.py` loading step.

## Demo URLs (these are made-up examples, do not visit them)

| URL | Expected |
|-----|----------|
| `https://www.wikipedia.org` | Legitimate |
| `https://github.com/python/cpython` | Legitimate |
| `http://paypal.com.secure-login.xyz/verify` | Phishing |
| `http://192.168.1.15/login/bank.php` | Phishing |
| `http://apple.com@ab12cd34.top/update` | Phishing |

## Limitations

- Looks only at URL text: no page content, domain age, WHOIS, SSL certificate or blacklist checks.
- Trained on a small, rule-generated sample, so it may not match real-world phishing.
- Keyword and subdomain logic is simplified (for example `.co.uk` domains are miscounted).
- Short, clean-looking phishing URLs and legitimate URLs with `login` or many digits can be misclassified.
- Not a real security tool.

## Future improvements

- Train on a large real dataset (for example 100k+ URLs).
- Add more features: domain age, entropy of the domain name, special characters, TLD type, path depth, brand-name-in-subdomain check.
- Add cross-validation and hyperparameter tuning.
- Check against blacklists such as Google Safe Browsing.
- Add a browser extension or REST API.

## Put it online (free, e.g. Render.com)

1. Upload the project folder to a GitHub repository (do not upload `venv/`).
2. On render.com: New > Web Service > connect the repository.
3. Build command: `pip install -r requirements.txt && python train.py`
4. Start command: `gunicorn app:app`
5. Deploy. Render gives you a public link like `https://your-app.onrender.com`.

The free tier sleeps after inactivity, so the first page load can take around 30-60 seconds.
