"""
features.py
-----------
Turns a URL (plain text) into a list of numbers that a machine learning
model can understand. We only look at the URL text itself (lexical features),
so no internet connection is needed.
"""

import re
from urllib.parse import urlparse

# Words that phishing pages often put in their URLs to look trustworthy
SUSPICIOUS_WORDS = ["login", "verify", "secure", "update", "bank", "account"]

# Popular URL shortener services (they hide the real destination)
SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly", "cutt.ly", "rebrand.ly"]

# The order of this list is IMPORTANT: the model is trained with features in
# exactly this order, and the web app must use the same order.
FEATURE_NAMES = [
    "url_length",
    "num_dots",
    "num_hyphens",
    "num_digits",
    "has_at_symbol",
    "has_ip_address",
    "uses_https",
    "num_subdomains",
    "num_suspicious_words",
    "uses_shortener",
]


def extract_features(url):
    """Take one URL string and return a dictionary {feature_name: number}."""
    url = str(url).strip()
    url_lower = url.lower()

    # urlparse only splits the URL properly if it starts with http:// or https://
    # If the user typed "example.com/login", we add "http://" in front.
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        parsed = urlparse("http://" + url)
    else:
        parsed = urlparse(url)

    # The domain part, e.g. "secure.paypal.com" (without port number)
    host = (parsed.hostname or "").lower()

    # 1. Is the "domain" actually an IP address like 192.168.1.1 ?
    has_ip = 1 if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host) else 0

    # 2. Count subdomains: "a.b.example.com" -> parts = [a, b, example, com]
    #    domain + extension are 2 parts, everything before them is a subdomain.
    #    (Simplified: it is not exact for endings like ".co.uk".)
    if has_ip or host == "":
        num_subdomains = 0
    else:
        num_subdomains = max(len(host.split(".")) - 2, 0)

    # 3. Does the URL use a known shortener?
    uses_shortener = 1 if host in SHORTENERS else 0

    features = {
        "url_length": len(url),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(ch.isdigit() for ch in url),
        "has_at_symbol": 1 if "@" in url else 0,
        "has_ip_address": has_ip,
        "uses_https": 1 if parsed.scheme == "https" else 0,
        "num_subdomains": num_subdomains,
        "num_suspicious_words": sum(url_lower.count(w) for w in SUSPICIOUS_WORDS),
        "uses_shortener": uses_shortener,
    }
    return features


def features_as_list(url):
    """Same as extract_features, but returns a list in FEATURE_NAMES order."""
    f = extract_features(url)
    return [f[name] for name in FEATURE_NAMES]


# Quick self-test: run "python features.py" to see the features of a few URLs
if __name__ == "__main__":
    tests = [
        "https://www.google.com",
        "http://192.168.10.5/secure-login/verify.php",
        "http://paypal.account-verify.secure-update.example.com/login@evil",
        "https://bit.ly/3xYz",
    ]
    for t in tests:
        print(t)
        print("  ", extract_features(t))
