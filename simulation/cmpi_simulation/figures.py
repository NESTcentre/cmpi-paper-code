"""Figure generation: A (CMPI vs param), B (ARI vs param)"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Bump in-figure text up so axis labels, tick labels, titles, and legends remain
# readable when the figure is rendered into the supplementary PDF at \linewidth.
plt.rcParams.update({
    "axes.labelsize":  14,
    "axes.titlesize":  14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 11,
    "figure.titlesize": 16,
})

ALGORITHMS = ["lfa", "leiden", "kmeans"]
ALGO_LABEL = {"lfa": "LFA", "leiden": "Leiden", "kmeans": "k-means"}
ALGO_XLABEL = {
    "lfa": "LFA cosine threshold",
    "leiden": "Leiden edge-similarity threshold",
    "kmeans": "k-means k",
}


def _read_aggregated(results_path: Path) -> list[dict]:
    return list(csv.DictReader(results_path.open()))


def _filter(rows, *, day_type: str, algorithm: str) -> list[dict]:
    out = [r for r in rows if r["day_type"] == day_type and r["algorithm"] == algorithm]
    out.sort(key=lambda r: float(r["parameter"]) if r["parameter"] else 0.0)
    return out


def _oracle_value(rows, *, day_type: str, col: str, stat: str = "mean") -> float:
    for r in rows:
        if r["day_type"] == day_type and r["algorithm"] == "oracle":
            return float(r[f"{col}_{stat}"])
    raise KeyError(f"No oracle row for {day_type}")


def figure_a(*, results_path: Path, out_path: Path) -> None:
    """CMPI vs algorithm parameter, faceted by day-type (rows) and algorithm (cols).

    Mean as a solid line, +/- 1 SD as a translucent shaded band.
    """
    rows = _read_aggregated(results_path)
    fig, axes = plt.subplots(2, len(ALGORITHMS), figsize=(5 * len(ALGORITHMS), 9), sharey="row")
    days = ["low_cmpi", "high_cmpi"]
    for i, day in enumerate(days):
        for j, algo in enumerate(ALGORITHMS):
            ax = axes[i][j]
            sub = _filter(rows, day_type=day, algorithm=algo)
            xs = np.array([float(r["parameter"]) for r in sub])
            paper_mean = np.array([float(r["cmpi_paper_mean"]) for r in sub])
            paper_sd = np.array([float(r["cmpi_paper_sd"]) for r in sub])
            alt_mean = np.array([float(r["cmpi_alt_mean"]) for r in sub])
            alt_sd = np.array([float(r["cmpi_alt_sd"]) for r in sub])

            ax.plot(xs, paper_mean, label="Proportion-based salience", marker="o", color="tab:blue")
            ax.fill_between(xs, paper_mean - paper_sd, paper_mean + paper_sd,
                            color="tab:blue", alpha=0.20, linewidth=0)

            ax.plot(xs, alt_mean, label="Position-weighted salience", marker="s", color="tab:orange")
            ax.fill_between(xs, alt_mean - alt_sd, alt_mean + alt_sd,
                            color="tab:orange", alpha=0.20, linewidth=0)

            oracle_paper = _oracle_value(rows, day_type=day, col="cmpi_paper")
            ax.axhline(oracle_paper, linestyle="--", color="tab:blue", alpha=0.7,
                       label="Oracle (proportion-based)")
            oracle_alt_mean = _oracle_value(rows, day_type=day, col="cmpi_alt")
            ax.axhline(oracle_alt_mean, linestyle="--", color="tab:orange", alpha=0.7,
                       label="Oracle (position-weighted)")
            ax.set_xlabel(ALGO_XLABEL[algo])
            if j == 0:
                ax.set_ylabel("CMPI")
            ax.set_title(f"{day.replace('_', '-')} day, {ALGO_LABEL[algo]}")
            if i == 0 and j == 0:
                ax.legend(loc="upper left")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)


def figure_b(*, results_path: Path, out_path: Path) -> None:
    """ARI vs algorithm parameter. Mean line + empirical min-max shaded band across replicates."""
    rows = _read_aggregated(results_path)
    fig, axes = plt.subplots(2, len(ALGORITHMS), figsize=(5 * len(ALGORITHMS), 7), sharey="row")
    days = ["low_cmpi", "high_cmpi"]
    for i, day in enumerate(days):
        for j, algo in enumerate(ALGORITHMS):
            ax = axes[i][j]
            sub = _filter(rows, day_type=day, algorithm=algo)
            xs = np.array([float(r["parameter"]) for r in sub])
            ari_mean = np.array([float(r["ari_mean"]) for r in sub])
            ari_min = np.array([float(r["ari_min"]) for r in sub])
            ari_max = np.array([float(r["ari_max"]) for r in sub])
            ax.plot(xs, ari_mean, marker="o", color="tab:green")
            # ARI is bounded at 1.0 from above; report empirical min-max range across the
            # 10 replicates rather than mean +/- SD, so the band is bounded by data and
            # cannot exceed the theoretical maximum.
            ax.fill_between(xs, ari_min, ari_max,
                            color="tab:green", alpha=0.20, linewidth=0)
            ax.axhline(1.0, linestyle="--", color="grey", alpha=0.6)
            ax.set_xlabel(ALGO_XLABEL[algo])
            if j == 0:
                ax.set_ylabel("ARI")
            ax.set_ylim(-0.05, 1.05)
            ax.set_title(f"{day.replace('_', '-')} day, {ALGO_LABEL[algo]}")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)

