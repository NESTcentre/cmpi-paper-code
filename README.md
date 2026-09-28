# Code for "A generalisable framework for context-aware measurement of media presence"

Code accompanying Mastitsky et al. (2026), *A generalisable framework for context-aware measurement of
media presence*, Computational Communication Research.

It reproduces every figure and table in the paper, every statistic the paper
computes from the shared data, and all results in its Supplementary.

| Folder | Language | Reproduces |
|---|---|---|
| [`analysis/`](analysis) | R | Figures 1–4, Table 1, and the statistics quoted in the text |
| [`simulation/`](simulation) | Python | The clustering-sensitivity simulation in the Supplementary |

## Data

The analysis reads the published datasets directly from figshare (CC BY 4.0).
Each file is pinned to the version used in the paper and checked against its
published MD5 checksum on download.

| Dataset | DOI | Used for |
|---|---|---|
| Time series of media presence for twelve European politicians in Russian–language media (2025) | [10.6084/m9.figshare.31094134](https://doi.org/10.6084/m9.figshare.31094134) | Figures 2 and 4, statistics |
| Grouped counts of news articles mentioning European politicians in Russian–language media (2025) | [10.6084/m9.figshare.31094176](https://doi.org/10.6084/m9.figshare.31094176) | Figure 3 (ICC), statistics |
| Daily mention counts for twelve European politicians in Russian–language media (2025) | [10.6084/m9.figshare.34015302](https://doi.org/10.6084/m9.figshare.34015302) | Figure 4 (simple proportion, ξ), statistics |

These are processed data. They come from one specific instantiation of the
CMPI framework: the media-monitoring system of the New Eurasian Strategies
Centre. The system is proprietary, so its source documents, architecture and
parameters are not included here. The paper describes its main processing
stages.

The simulation's synthetic corpora and results are included in
[`simulation/`](simulation).

## Reproducing the analysis (R)

Requirements: R 4.5.0, and a build of R with Cairo support (standard on
macOS, Linux and Windows builds from CRAN). Package versions are pinned in
[`analysis/renv.lock`](analysis/renv.lock); restore them with
[renv](https://rstudio.github.io/renv/):

```bash
cd analysis
Rscript -e 'install.packages("renv"); renv::restore(lockfile = "renv.lock")'
Rscript run_all.R
```

`run_all.R` downloads the data (about 1.3 MB) into `data-cache/`, writes the
four figures to `output/`, and prints every statistic the paper computes from
these data next to the value the paper reports. Each script can also be run on its own:

| Script | Output | In the paper |
|---|---|---|
| `figure_1.R` | `output/fig1_upper_bound.pdf` | Figure 1 |
| `figure_2.R` | `output/fig2_cmpi_timeseries.pdf` | Figure 2 |
| `figure_3.R` | `output/fig3_icc.pdf` | Figure 3 and the ICC analysis |
| `figure_4.R` | `output/fig4_cmpi_vs_proportion.pdf` | Figure 4 and the ξ coefficients |
| `table_1.R` | printed table | Table 1 |
| `numbers.R` | printed statistics | All statistics computed from the data, and Table 1 |

Figures use the Noto Sans font, bundled in `analysis/fonts/` under the SIL Open
Font License, so the figures don't depend on the fonts installed on your system. Chatterjee's ξ is computed
with a fixed random seed, because `XICOR::calculateXI()` breaks ties at random.

Runtime: about 15 seconds on an Apple M3 Pro, including the downloads.

## Reproducing the simulation (Python)

See [`simulation/README.md`](simulation/README.md). With
[uv](https://docs.astral.sh/uv/) installed:

```bash
cd simulation
uv sync --frozen
uv run --frozen python -m cmpi_simulation.run
```

This re-runs the whole simulation on the included synthetic corpora and
reproduces the Supplementary's results files exactly. Runtime: about 2 minutes on an
Apple M3 Pro, plus a one-off download of the sentence-embedding model.

## Computing environment

All results were produced on an Apple M3 Pro (12 cores, 36 GB RAM) running
macOS 26.3, with R 4.5.0 and Python 3.11 (via uv).

## Licence

- Code: [MIT](LICENSE).
- Simulation corpora and results in `simulation/data/` and `simulation/data_large/`: CC BY 4.0.
- Noto Sans font in `analysis/fonts/`: [SIL Open Font License 1.1](analysis/fonts/OFL.txt).

## Citation

If you use this code, please cite the paper and this code archive:

- Paper: Mastitsky, S. E., Rey Lago, D., Shcherbakova, P., Glod, K., Kontzedakis, D., & Blyzniuk, B. V. (2026). A generalisable framework for context-aware measurement of media presence. *Computational Communication Research*. DOI to be added.
- Code: Zenodo, DOI to be added.
