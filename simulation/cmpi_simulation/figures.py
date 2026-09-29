"""Figure generation: A (CMPI vs param), B (ARI vs param)"""

import csv
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from . import config as cfg

# Figures are drawn at the width of the journal's text column, in Noto Sans
# (bundled in analysis/fonts/), with text just under the caption size. This
# matches the figures of the main paper (see analysis/R/setup.R).
FONT = "Noto Sans"
WIDTH_IN = 312.92813 / 72.27  # text-column width of the CCR template, in inches
TEXT_PT = 6.5                 # labels
TICK_PT = 5.5                 # axis numbers

# Font subsetting on PDF export logs every step at INFO level.
logging.getLogger("fontTools").setLevel(logging.WARNING)

for _font in sorted(cfg.FONTS_DIR.glob("*.ttf")):
    font_manager.fontManager.addfont(str(_font))

plt.rcParams.update({
    "font.family":     FONT,
    "font.size":       TEXT_PT,
    "axes.labelsize":  TEXT_PT,
    "axes.titlesize":  TEXT_PT,
    "xtick.labelsize": TICK_PT,
    "ytick.labelsize": TICK_PT,
    "legend.fontsize": TEXT_PT,
    "axes.linewidth":  0.4,
    "xtick.major.width": 0.4,
    "ytick.major.width": 0.4,
    "xtick.major.size":  2,
    "ytick.major.size":  2,
    "lines.linewidth":   0.8,
    "lines.markersize":  2.5,
    "pdf.fonttype":      42,  # embed TrueType, keeps text selectable
})

# Reproducible files: no creation date or software version in the metadata.
PDF_METADATA = {"CreationDate": None, "Producer": None, "Creator": None}
PNG_METADATA = {"Software": None}

ALGORITHMS = ["lfa", "leiden", "kmeans"]
ALGO_LABEL = {"lfa": "Leader–follower", "leiden": "Leiden", "kmeans": "k-means"}
ALGO_XLABEL = {
    "lfa": "Similarity threshold τ",
    "leiden": "Edge–admission threshold τ",
    "kmeans": "Number of clusters k",
}
DAYS = ["low_cmpi", "high_cmpi"]
DAY_LABEL = {"low_cmpi": "Low–presence day", "high_cmpi": "High–presence day"}


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


def _label_panel(ax, *, i: int, j: int, algo: str, day: str, metric: str) -> None:
    """Algorithm names above the top row, day names in the first column's y label."""
    if i == 0:
        ax.set_title(ALGO_LABEL[algo])
    if i == len(DAYS) - 1:
        ax.set_xlabel(ALGO_XLABEL[algo])
    if j == 0:
        ax.set_ylabel(f"{DAY_LABEL[day]}\n{metric}")
    ax.grid(axis="y", color="0.9", linewidth=0.3)
    ax.set_axisbelow(True)


def _save(fig, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, metadata=PNG_METADATA)
    fig.savefig(out_path.with_suffix(".pdf"), metadata=PDF_METADATA)
    plt.close(fig)


def figure_a(*, results_path: Path, out_path: Path) -> None:
    """CMPI vs algorithm parameter, faceted by day-type (rows) and algorithm (cols).

    Mean as a solid line, +/- 1 SD as a translucent shaded band.
    """
    rows = _read_aggregated(results_path)
    fig, axes = plt.subplots(2, len(ALGORITHMS), figsize=(WIDTH_IN, 3.3),
                             sharey="row", layout="constrained")
    for i, day in enumerate(DAYS):
        for j, algo in enumerate(ALGORITHMS):
            ax = axes[i][j]
            sub = _filter(rows, day_type=day, algorithm=algo)
            xs = np.array([float(r["parameter"]) for r in sub])
            paper_mean = np.array([float(r["cmpi_paper_mean"]) for r in sub])
            paper_sd = np.array([float(r["cmpi_paper_sd"]) for r in sub])
            alt_mean = np.array([float(r["cmpi_alt_mean"]) for r in sub])
            alt_sd = np.array([float(r["cmpi_alt_sd"]) for r in sub])

            ax.plot(xs, paper_mean, label="Proportion–based salience", marker="o", color="tab:blue")
            ax.fill_between(xs, paper_mean - paper_sd, paper_mean + paper_sd,
                            color="tab:blue", alpha=0.20, linewidth=0)

            ax.plot(xs, alt_mean, label="Position–weighted salience", marker="s", color="tab:orange")
            ax.fill_between(xs, alt_mean - alt_sd, alt_mean + alt_sd,
                            color="tab:orange", alpha=0.20, linewidth=0)

            oracle_paper = _oracle_value(rows, day_type=day, col="cmpi_paper")
            ax.axhline(oracle_paper, linestyle="--", color="tab:blue", alpha=0.7,
                       label="Oracle (proportion–based)")
            oracle_alt_mean = _oracle_value(rows, day_type=day, col="cmpi_alt")
            ax.axhline(oracle_alt_mean, linestyle="--", color="tab:orange", alpha=0.7,
                       label="Oracle (position–weighted)")
            _label_panel(ax, i=i, j=j, algo=algo, day=day, metric="CMPI")
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncols=2, frameon=False)
    _save(fig, out_path)


def figure_b(*, results_path: Path, out_path: Path) -> None:
    """ARI vs algorithm parameter. Mean line + empirical min-max shaded band across replicates."""
    rows = _read_aggregated(results_path)
    fig, axes = plt.subplots(2, len(ALGORITHMS), figsize=(WIDTH_IN, 2.7),
                             sharey="row", layout="constrained")
    for i, day in enumerate(DAYS):
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
            ax.set_ylim(-0.05, 1.05)
            _label_panel(ax, i=i, j=j, algo=algo, day=day, metric="ARI")
    _save(fig, out_path)
