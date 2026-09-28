# Recomputes the statistics quoted in the text of the paper from the published
# figshare datasets, and prints them next to the values the paper reports.

source("R/setup.R")
suppressPackageStartupMessages(library(lme4))

report <- function(what, value, paper) {
  cat(sprintf("  %-58s %-22s paper: %s\n", what, value, paper))
}

cmpi <- read_figshare("cmpi")
props <- read_figshare("proportions")
icc_data <- read_figshare("icc")

# ------------------------------------------------------------------------------
cat("\nValidation data: CMPI time series (Figure 2)\n")
medians <- cmpi |> group_by(politician) |> summarise(m = median(cmpi)) |> arrange(-m)
report("Politicians, ordered by median CMPI",
       paste(head(medians$politician, 3), collapse = ", "), "Macron, Merz, Starmer highest")
for (i in seq_len(nrow(medians))) {
  report(paste0("  median CMPI, ", medians$politician[i]), sprintf("%.3f", medians$m[i]), "Figure 2")
}
tusk <- cmpi |> filter(politician == "D. Tusk") |> arrange(report_date)
sep10 <- tusk$cmpi[tusk$report_date == as.Date("2025-09-10")]
before <- median(tusk$cmpi[tusk$report_date >= as.Date("2025-08-27") & tusk$report_date < as.Date("2025-09-10")])
report("Tusk CMPI on 10 Sep 2025 / median of the 14 days before",
       sprintf("%.1f times", sep10 / before), "an order of magnitude")

# ------------------------------------------------------------------------------
cat("\nICC of entity salience within stories (Figure 3)\n")
icc_of <- function(d) {
  fit <- glmer(cbind(m_g, n_g - m_g) ~ 1 + (1 | contextual_cluster),
               data = d, family = binomial(link = "logit"), nAGQ = 1)
  mlmhelpr::icc(fit)$icc
}
icc <- icc_data |>
  group_by(politician, report_date) |>
  reframe(icc = suppressMessages(suppressWarnings(icc_of(pick(everything())))))
singular <- icc |> filter(icc <= 0) |> count(politician)
report("Politician-date models fitted", nrow(icc), "")
report("Singular fits (not shown)",
       paste(sprintf("%s %d", singular$politician, singular$n), collapse = ", "),
       "Orpo 1, Michal 1, Silina 2")
icc_medians <- icc |> filter(icc > 0) |> group_by(politician) |> summarise(m = median(icc))
report("Range of per-politician median ICC",
       sprintf("%.3f to %.3f", min(icc_medians$m), max(icc_medians$m)), "0.466 to 0.834")
largest <- icc_data |>
  group_by(politician, report_date) |> summarise(n_max = max(n_g), .groups = "drop") |>
  group_by(politician) |> summarise(typical_largest_cluster = median(n_max))
for (who in c("P. Orpo", "K. Michal", "G. Nausėda", "E. Macron", "F. Merz", "K. Starmer")) {
  report(paste0("  typical largest daily cluster, ", who),
         largest$typical_largest_cluster[largest$politician == who],
         if (who %in% c("P. Orpo", "K. Michal", "G. Nausėda")) "fewer than 100" else "closer to 200")
}

# ------------------------------------------------------------------------------
cat("\nCMPI and the simple proportion of mentions (Figure 4)\n")
dat <- inner_join(cmpi, props, by = c("politician", "report_date"))
set.seed(2026)  # same seed as figure_4.R: ties in x are broken at random
xi <- dat |>
  group_by(politician) |>
  summarise(xi = suppressWarnings(XICOR::calculateXI(proportion, cmpi)), .groups = "drop")
report("Chatterjee's xi, range", sprintf("%.3f to %.3f", min(xi$xi), max(xi$xi)), "0.616 to 0.816")
report("Chatterjee's xi, median", sprintf("%.3f", median(xi$xi)), "0.697")

cat("\n  Events: rank of each day within the politician's year (1 = highest)\n")
ranked <- dat |>
  group_by(politician) |>
  mutate(cmpi_rank = rank(-cmpi), proportion_rank = rank(-proportion)) |>
  ungroup()
events <- tibble::tribble(
  ~politician,  ~event,        ~note,
  "E. Macron",  "2025-03-05",  "national address; CMPI peaked the following day",
  "F. Merz",    "2025-05-28",  "pledge of support after meeting Zelenskyy",
  "K. Starmer", "2025-03-02",  "missile deal; CMPI peaked the following day"
)
for (i in seq_len(nrow(events))) {
  e <- as.Date(events$event[i])
  window <- ranked |>
    filter(politician == events$politician[i], report_date >= e - 3, report_date <= e + 4) |>
    select(report_date, cmpi, cmpi_rank, proportion, proportion_rank)
  cat(sprintf("\n  %s, event on %s (%s)\n", events$politician[i], events$event[i], events$note[i]))
  print(as.data.frame(window |> mutate(cmpi = round(cmpi, 2), proportion = round(proportion, 3))),
        row.names = FALSE)
}

# ------------------------------------------------------------------------------
source("table_1.R")
