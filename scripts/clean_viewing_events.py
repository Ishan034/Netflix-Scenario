"""Clean the Netflix viewing-events export against the title catalog and split train/holdout.

Usage: python scripts/clean_viewing_events.py EVENTS_CSV CATALOG_CSV OUT_DIR
"""
import sys
import pandas as pd

events_path, catalog_path, out_dir = sys.argv[1:4]
SPLIT_DATE = "2026-11-10"          # holdout = this date and later
LOW_COMPLETED_RATIO = 0.20         # completed but watched < 20% of runtime -> drop
MAX_WATCH_SECONDS = 30_000         # natural gap in data: nothing between 3,600s and 31,300s

e = pd.read_csv(events_path, dtype=str, keep_default_na=False)
c = pd.read_csv(catalog_path, dtype=str, keep_default_na=False)
e = e.apply(lambda s: s.str.strip())
log = [("raw export", len(e))]

# 1. required fields present
req = ["title_id", "watch_seconds", "completed", "device_type", "country"]
e = e[(e[req] != "").all(axis=1)]
log.append(("after dropping empty required fields", len(e)))

# 2. title must exist in catalog with a usable runtime
cat = c[["title_id", "runtime_minutes"]].copy()
cat["runtime_s"] = pd.to_numeric(cat.runtime_minutes, errors="coerce") * 60
e = e[e.title_id.isin(cat.title_id)]
log.append(("after dropping titles not in catalog", len(e)))
e = e.merge(cat[["title_id", "runtime_s"]], on="title_id", how="left")
e = e[e.runtime_s.notna() & (e.runtime_s > 0)]
log.append(("after dropping titles with no catalog runtime", len(e)))

ws = pd.to_numeric(e.watch_seconds, errors="coerce")
e = e[ws.notna()]; ws = ws[ws.notna()]

# 3. completed with implausibly little watch time
bad = (e.completed == "True") & (ws / e.runtime_s < LOW_COMPLETED_RATIO)
e, ws = e[~bad], ws[~bad]
log.append((f"after dropping completed rows < {LOW_COMPLETED_RATIO:.0%} of runtime", len(e)))

# 4. impossible watch time
e = e[ws <= MAX_WATCH_SECONDS]
log.append((f"after dropping watch_seconds > {MAX_WATCH_SECONDS}", len(e)))

e = e.drop(columns="runtime_s").sort_values(["event_datetime", "event_id"])
train = e[e.event_datetime < SPLIT_DATE]
hold = e[e.event_datetime >= SPLIT_DATE]
train.to_csv(f"{out_dir}/viewing_events_train.csv", index=False)
hold.to_csv(f"{out_dir}/viewing_events_holdout.csv", index=False)

for k, v in log:
    print(f"{v:>5}  {k}")
for name, d in [("train", train), ("holdout", hold)]:
    print(f"{name}: {len(d)} rows, {d.event_datetime.min()} to {d.event_datetime.max()}")
