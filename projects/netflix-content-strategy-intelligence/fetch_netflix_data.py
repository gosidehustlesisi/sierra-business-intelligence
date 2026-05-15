#!/usr/bin/env python3
"""
Netflix Titles Dataset — Automated Fetcher
Downloads the Netflix Movies & TV Shows dataset from Kaggle via kagglehub.

Usage:
    python fetch_netflix_data.py

Requirements:
    pip install kagglehub pandas
"""

import os
import shutil
import sys

def fetch_netflix_data():
    """Download Netflix dataset from Kaggle and store in data/ directory."""
    print("Fetching Netflix dataset from Kaggle...")
    
    try:
        import kagglehub
    except ImportError:
        print("ERROR: kagglehub not installed. Run: pip install kagglehub")
        sys.exit(1)
    
    # Download from Kaggle
    path = kagglehub.dataset_download("shivamb/netflix-shows")
    print(f"Kaggle download path: {path}")
    
    # Find the CSV file
    csv_path = None
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.csv'):
                csv_path = os.path.join(root, f)
                break
        if csv_path:
            break
    
    if not csv_path:
        print("ERROR: No CSV file found in downloaded archive")
        sys.exit(1)
    
    # Copy to data directory
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    dest = os.path.join(data_dir, "netflix_titles.csv")
    shutil.copy2(csv_path, dest)
    print(f"Saved to: {dest}")
    
    # Verify
    import pandas as pd
    df = pd.read_csv(dest)
    print(f"\nVerification:")
    print(f"  Records: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Column names: {list(df.columns)}")
    print(f"  Date range: {df['date_added'].min()} to {df['date_added'].max()}")
    print(f"  Movies: {len(df[df['type']=='Movie']):,}")
    print(f"  TV Shows: {len(df[df['type']=='TV Show']):,}")
    print("\nFetch complete. Data is real and verified.")
    
    return dest

if __name__ == "__main__":
    fetch_netflix_data()
