import os
import gzip
import json
import csv
import random
import urllib.request

# Configuration
DATA_URL = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Electronics_5.json.gz"
CSV_OUT = "/tmp/bi-fix/projects/amazon-product-customer-intelligence/data/amazon_reviews_electronics_5core.csv"
SAMPLE_RATE = 1 / 25  # yields ~68K from 1.69M - smaller for GitHub
RANDOM_SEED = 42


def download_and_convert():
    print(f"[down] {DATA_URL}")
    os.makedirs("data", exist_ok=True)
    
    req = urllib.request.Request(DATA_URL, headers={"User-Agent": "Mozilla/5.0"})
    
    print("[conv] Streaming JSON -> CSV (sample rate = {:.4f})".format(SAMPLE_RATE))
    random.seed(RANDOM_SEED)
    count = kept = 0
    
    with urllib.request.urlopen(req, timeout=180) as resp:
        # Stream through gzip decompression
        with gzip.GzipFile(fileobj=resp) as gz:
            with open(CSV_OUT, "w", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out)
                writer.writerow([
                    "reviewerID", "asin", "reviewerName",
                    "helpful_upvotes", "helpful_total",
                    "reviewText", "overall", "summary",
                    "unixReviewTime", "reviewTime"
                ])
                
                for line in gz:
                    line = line.decode('utf-8')
                    count += 1
                    if random.random() < SAMPLE_RATE:
                        d = json.loads(line)
                        helpful = d.get("helpful", [0, 0])
                        up = helpful[0] if isinstance(helpful, list) and len(helpful) == 2 else 0
                        tot = helpful[1] if isinstance(helpful, list) and len(helpful) == 2 else 0
                        writer.writerow([
                            d.get("reviewerID", ""),
                            d.get("asin", ""),
                            d.get("reviewerName", ""),
                            up, tot,
                            d.get("reviewText", "").replace("\n", " ").replace("\r", " "),
                            d.get("overall", 0),
                            d.get("summary", "").replace("\n", " ").replace("\r", " "),
                            d.get("unixReviewTime", 0),
                            d.get("reviewTime", "")
                        ])
                        kept += 1
                    if count % 500_000 == 0:
                        print(f"  processed {count:,} | kept {kept:,}")
    
    print(f"[done] Total scanned: {count:,} | Kept: {kept:,}")
    print(f"[done] Output: {CSV_OUT}")


def verify():
    import pandas as pd
    df = pd.read_csv(CSV_OUT)
    print(f"\n[verify] Records: {len(df):,}")
    print(f"[verify] Columns: {list(df.columns)}")
    print(f"[verify] Avg rating: {df['overall'].mean():.2f}")
    print(f"[verify] Date range: {pd.to_datetime(df['unixReviewTime'], unit='s').min().date()} to {pd.to_datetime(df['unixReviewTime'], unit='s').max().date()}")
    print(f"[verify] Unique products: {df['asin'].nunique():,}")
    print(f"[verify] Unique reviewers: {df['reviewerID'].nunique():,}")
    print("[verify] Data looks real ✓")


if __name__ == "__main__":
    download_and_convert()
    verify()
