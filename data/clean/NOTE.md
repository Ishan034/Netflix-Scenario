# Viewing events – cleaning & train/holdout split

**Key prompt:**
> "take into account the entire viewing events exports and compare it with the title catalog, then … remove any rows that have any of the important values such as title_id, watch_seconds, completed, device_type and country columns as empty, then remove any rows that don't have a corresponding title in the title catalog, remove any rows which have a very small watch seconds as compared to the title's length in the catalog but is still marked as completed, lastly remove any row which has a huge watch seconds that is impossible. … split the dataset from the exact date of November 10th … (November 10th should also fall in the holdout section)"

**Checks:** 5,000 raw rows → 4,300 clean. Removed: 254 with empty required fields, 170 with titles not in the catalog, 101 whose title has no runtime_minutes in the catalog, 133 marked completed at < 20% of runtime, and 42 with watch_seconds > 30,000 (the data has no events between 3,600 s and 31,300 s). Train = 3,982 rows (2026-08-17 → 2026-11-09); holdout = 318 rows (2026-11-10 → 2026-11-16). After the split, both files were re-checked: no blanks, no duplicate event_ids, every title_id in the catalog, and no row breaks a rule.

Reproduce: `python scripts/clean_viewing_events.py <events.csv> <catalog.csv> data/clean`
