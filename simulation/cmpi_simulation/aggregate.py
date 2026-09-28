"""Aggregate per-cell results across replicates: mean and SD per (day, algorithm, parameter)."""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

NUMERIC_COLS = ("recovered_K", "ari", "cmpi_paper", "cmpi_alt")


def aggregate(*, per_cell_path: Path, out_path: Path) -> None:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    with per_cell_path.open() as f:
        for row in csv.DictReader(f):
            key = (row["day_type"], row["algorithm"], row["parameter"])
            groups[key].append(row)

    out_rows = []
    for (day_type, algorithm, parameter), rows in sorted(groups.items()):
        out_row = {"day_type": day_type, "algorithm": algorithm, "parameter": parameter, "n_replicates": len(rows)}
        for col in NUMERIC_COLS:
            vals = [float(r[col]) for r in rows]
            out_row[f"{col}_mean"] = mean(vals)
            out_row[f"{col}_sd"] = stdev(vals) if len(vals) > 1 else 0.0
            out_row[f"{col}_min"] = min(vals)
            out_row[f"{col}_max"] = max(vals)
        out_rows.append(out_row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["day_type", "algorithm", "parameter", "n_replicates"] + [
        f"{col}_{stat}" for col in NUMERIC_COLS for stat in ("mean", "sd", "min", "max")
    ]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)
