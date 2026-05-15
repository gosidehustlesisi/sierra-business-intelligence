import pandas as pd
import os

DATA_DIR = "data"

# Clean worldwide interest over time
print("Cleaning worldwide data...")
df_ww = pd.read_csv(os.path.join(DATA_DIR, "interest_over_time_worldwide.csv"), index_col=0)
# Remove duplicate geo/fetched_at columns, keep only keyword columns
drop_cols = [c for c in df_ww.columns if c.startswith("geo") or c.startswith("fetched_at")]
df_ww_clean = df_ww.drop(columns=drop_cols)
df_ww_clean.index = pd.to_datetime(df_ww_clean.index)
df_ww_clean.to_csv(os.path.join(DATA_DIR, "interest_over_time_worldwide.csv"))
print(f"  Worldwide: {df_ww_clean.shape}")

# Clean US interest over time
df_us = pd.read_csv(os.path.join(DATA_DIR, "interest_over_time_us.csv"), index_col=0)
drop_cols = [c for c in df_us.columns if c.startswith("geo") or c.startswith("fetched_at")]
df_us_clean = df_us.drop(columns=drop_cols)
df_us_clean.index = pd.to_datetime(df_us_clean.index)
df_us_clean.to_csv(os.path.join(DATA_DIR, "interest_over_time_us.csv"))
print(f"  US: {df_us_clean.shape}")

# Clean region data — melt to long format
print("Cleaning region data...")
df_region = pd.read_csv(os.path.join(DATA_DIR, "interest_by_region_us.csv"))
# Each row has keyword column filled; melt to (geoName, geoCode, keyword, interest)
keyword_cols = ["AI", "machine learning", "ChatGPT", "Bitcoin", "Tesla", "Netflix", "Amazon",
                "telehealth", "mental health", "fitness", "inflation", "recession", "stock market", "crypto"]
meta_cols = ["geoName", "geoCode", "geo", "fetched_at"]
# We need to melt
id_vars = ["geoName", "geoCode", "geo", "fetched_at"]
value_vars = keyword_cols
# But many are NaN per row. Better: group by geo and keyword.
records = []
for _, row in df_region.iterrows():
    geo = row["geoName"]
    code = row["geoCode"]
    for kw in keyword_cols:
        val = row.get(kw)
        if pd.notna(val):
            records.append({
                "geoName": geo,
                "geoCode": code,
                "keyword": kw,
                "interest": int(val),
                "geo_scope": row.get("geo", "US"),
                "fetched_at": row.get("fetched_at")
            })
df_region_long = pd.DataFrame(records)
df_region_long.to_csv(os.path.join(DATA_DIR, "interest_by_region_us.csv"), index=False)
print(f"  Region (long): {df_region_long.shape}")

# Verify
print("\n--- Sample ---")
print(df_ww_clean.head())
print(df_region_long.head())
print("\nAll files cleaned and ready.")
