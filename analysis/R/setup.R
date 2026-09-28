# Shared setup for the analysis scripts: packages, data access, figure style.
# Scripts are run from the analysis/ directory (see run_all.R).

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(ggplot2)
})

# ------------------------------------------------------------------------------
# Data: the published figshare datasets, pinned to the exact files used in the
# paper. Files are downloaded once into data-cache/ and checked against the
# MD5 checksums figshare reports for them.
# ------------------------------------------------------------------------------

FIGSHARE <- list(
  cmpi = list(
    doi = "10.6084/m9.figshare.31094134.v1", file_id = 61111537,
    name = "mastitsky_et_al_2026_cmpi_data.csv",
    md5 = "88a1e05b61a1d88e3a8cde78c6d2d208"
  ),
  icc = list(
    doi = "10.6084/m9.figshare.31094176.v1", file_id = 61111756,
    name = "mastitsky_et_al_2026_icc_data.csv",
    md5 = "76d25b64c2d2163fb25c65f1ba062e2b"
  ),
  proportions = list(
    doi = "10.6084/m9.figshare.34015302.v1", file_id = 69429879,
    name = "mastitsky_et_al_2026_proportions_data.csv",
    md5 = "9709125321823128808ffccf23f000db"
  )
)

read_figshare <- function(dataset) {
  f <- FIGSHARE[[dataset]]
  dir.create("data-cache", showWarnings = FALSE)
  path <- file.path("data-cache", f$name)
  if (!file.exists(path)) {
    message("Downloading ", f$name, " (doi:", f$doi, ")")
    download.file(sprintf("https://ndownloader.figshare.com/files/%d", f$file_id),
                  path, mode = "wb", quiet = TRUE)
  }
  if (unname(tools::md5sum(path)) != f$md5) {
    stop(f$name, " does not match the published file (MD5 mismatch). ",
         "Delete data-cache/ and run again.")
  }
  read_csv(path, show_col_types = FALSE)
}

# ------------------------------------------------------------------------------
# Figure style: figures are drawn at the width of the journal's text column,
# in Noto Sans (bundled in fonts/), with text just under the caption size.
# ------------------------------------------------------------------------------

FONT <- "Noto Sans"
WIDTH_IN <- 312.92813 / 72.27  # text-column width of the CCR template, in inches
TEXT_PT <- 6.5                 # labels
TICK_PT <- 5.5                 # axis numbers and value labels

# Make the bundled fonts visible to the Cairo PDF device without installing
# them system-wide. This must run before the first Cairo call.
local({
  fc_file <- tempfile(fileext = ".conf")
  writeLines(c(
    '<?xml version="1.0"?>',
    '<!DOCTYPE fontconfig SYSTEM "fonts.dtd">',
    "<fontconfig>",
    sprintf('  <include ignore_missing="yes">%s</include>',
            file.path(R.home(), "fontconfig/fonts/fonts.conf")),
    '  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>',
    sprintf("  <dir>%s</dir>", normalizePath("fonts")),
    "</fontconfig>"
  ), fc_file)
  Sys.setenv(FONTCONFIG_FILE = fc_file)
})

figure_style <- theme(
  text = element_text(family = FONT, size = TEXT_PT),
  axis.text = element_text(size = TICK_PT),
  axis.title = element_text(size = TEXT_PT),
  strip.text = element_text(size = TEXT_PT),
  legend.text = element_text(size = TICK_PT),
  legend.title = element_text(size = TEXT_PT),
  axis.ticks = element_line(linewidth = 0.25),
  axis.ticks.length = unit(0.1, "cm")
)

save_figure <- function(plot, file, height) {
  dir.create("output", showWarnings = FALSE)
  ggsave(file.path("output", file), plot = plot,
         width = WIDTH_IN, height = height, units = "in", device = cairo_pdf)
  message("Saved output/", file)
}

# Per-panel y axes that run from 0 to a round top value, so the 0 and top
# gridlines line up across panels even though each panel has its own scale.
aligned_y_axis <- function(n_breaks, expand) {
  breaks_by_top <- new.env()
  limits <- function(l) {
    br <- pretty(c(0, l[2]), n = n_breaks)
    assign(format(max(br)), br, envir = breaks_by_top)  # reused by breaks()
    range(br)
  }
  breaks <- function(l) {
    # ggplot passes the range with its margins added; recover the top
    top <- l[2] - expand[2] * (l[2] - l[1]) / (1 + sum(expand))
    get(format(signif(top, 10)), envir = breaks_by_top)
  }
  scale_y_continuous(limits = limits, breaks = breaks, expand = expansion(mult = expand))
}
