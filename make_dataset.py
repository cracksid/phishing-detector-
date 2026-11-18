"""
make_dataset.py
---------------
Creates a small SAMPLE dataset (urls.csv) with ~1000 URLs:
  label 0 = legitimate, label 1 = phishing

Why? So the project runs without downloading anything.
NOTE: this data is made up by rules + some random noise. It is only for
learning/demo. For your final report, you can replace urls.csv with a real
dataset that has two columns: "url" and "label" (0 = legitimate, 1 = phishing).
"""

import random
import pandas as pd

random.seed(42)  # same random numbers every time -> same dataset every run

BRANDS = ["paypal", "amazon", "netflix", "apple", "microsoft", "google",
          "facebook", "instagram", "sbi", "hdfcbank", "icici", "dropbox"]
GOOD_SITES = ["wikipedia.org", "github.com", "stackoverflow.com", "bbc.com",
              "nytimes.com", "python.org", "coursera.org", "medium.com",
              "linkedin.com", "youtube.com", "amazon.in", "flipkart.com",
              "irctc.co.in", "mit.edu", "nasa.gov", "reddit.com",
              "paypal.com", "microsoft.com", "apple.com", "hdfcbank.com"]
WORDS = ["news", "docs", "article", "product", "help", "blog", "course",
         "item", "page", "profile", "search", "download", "events"]
KEYWORDS = ["login", "verify", "secure", "update", "bank", "account"]
BAD_TLDS = ["xyz", "top", "tk", "info", "club", "online", "site", "ml"]
SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd"]


def rand_chars(n):
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(n))


def legit_url():
    site = random.choice(GOOD_SITES)
    scheme = "https" if random.random() < 0.9 else "http"
    sub = random.choice(["", "www.", "www.", "docs.", "blog.", "mail.", "support.", "en.m."])
    path = "/".join(random.choice(WORDS) for _ in range(random.randint(0, 3)))
    # Real sites sometimes have hyphens, digits, long paths and even "login" pages
    if random.random() < 0.15:
        path += "/" + random.choice(WORDS) + "-" + random.choice(WORDS) + "-" + str(random.randint(1, 2024))
    if random.random() < 0.10:
        path = random.choice(["login", "account/settings", "secure/checkout", "update-profile"])
    if random.random() < 0.05:   # some real URLs carry long numeric ids
        return f"{scheme}://{sub}{site}/{path}?id={random.randint(100, 99999)}"
    return f"{scheme}://{sub}{site}/{path}".rstrip("/")


def phishing_url():
    brand = random.choice(BRANDS)
    kw = random.choice(KEYWORDS)
    tld = random.choice(BAD_TLDS)
    scheme = "https" if random.random() < 0.45 else "http"
    kind = random.random()

    if kind < 0.20:      # IP address instead of a domain
        ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        return f"http://{ip}/{kw}/{brand}/{rand_chars(6)}.php"
    if kind < 0.40:      # brand name stuffed into subdomains
        return f"{scheme}://{brand}.com.{kw}-{rand_chars(4)}.{tld}/{kw}"
    if kind < 0.55:      # '@' trick: browser ignores everything before '@'
        return f"{scheme}://{brand}.com@{rand_chars(8)}.{tld}/{kw}"
    if kind < 0.70:      # shortened link
        return f"{scheme}://{random.choice(SHORTENERS)}/{rand_chars(6)}"
    if kind < 0.90:      # hyphen-heavy fake domain
        return f"{scheme}://{brand}-{kw}-{random.choice(KEYWORDS)}.{tld}/{rand_chars(5)}/{kw}.html"
    # Hard cases: short, clean-looking phishing URLs
    return f"{scheme}://{brand}{random.randint(1, 99)}.{random.choice(['com', tld])}/{rand_chars(5)}"


def main(n_each=500):
    rows = [(legit_url(), 0) for _ in range(n_each)]
    rows += [(phishing_url(), 1) for _ in range(n_each)]
    df = pd.DataFrame(rows, columns=["url", "label"])
    df = df.drop_duplicates().sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv("urls.csv", index=False)
    print(f"Saved urls.csv with {len(df)} rows")
    print(df["label"].value_counts().rename({0: "legitimate", 1: "phishing"}))
    print(df.head(6).to_string())


if __name__ == "__main__":
    main()
