# Figure 3: Intraclass Correlation Coefficient (ICC) of entity salience within
# stories. For each politician-date pair, a logistic random-intercept model
# (lme4::glmer, default settings) is fitted to the cluster-level counts, and the
# ICC is extracted with mlmhelpr::icc(). Singular fits (ICC = 0) are not shown.
#
# The politician-date pairs were selected when the figshare dataset was
# prepared, from data that are not public: for each politician, the up to 20
# dates with the most contextual clusters, excluding dates on which salience
# is constant across all clusters (the between-cluster variance cannot be
# estimated there). The dataset contains only the selected pairs, so the
# selection is not repeated here; the check below confirms the file meets it.

source("R/setup.R")
suppressPackageStartupMessages(library(lme4))

dat <- read_figshare("icc")

stopifnot(
  "more than 20 dates for a politician" =
    all(table(unique(dat[c("politician", "report_date")])$politician) <= 20),
  "a date with constant salience across clusters" =
    all(tapply(dat$m_g / dat$n_g, paste(dat$politician, dat$report_date),
               function(s) length(unique(s)) > 1))
)

icc_of <- function(d) {
  fit <- glmer(cbind(m_g, n_g - m_g) ~ 1 + (1 | contextual_cluster),
               data = d, family = binomial(link = "logit"), nAGQ = 1)
  mlmhelpr::icc(fit)$icc
}

icc <- dat |>
  group_by(politician, report_date) |>
  reframe(icc = suppressMessages(suppressWarnings(icc_of(pick(everything())))))

shown <- icc |> filter(icc > 0)

medians <- shown |>
  group_by(politician) |>
  summarise(med = median(icc, na.rm = TRUE))

p <- shown |>
  ggplot(aes(reorder(politician, icc, FUN = median, na.rm = TRUE), icc)) +
  geom_point(alpha = 0.25, shape = 16) +
  geom_point(data = medians, aes(politician, med), shape = 4, size = 2, stroke = 0.8) +
  coord_flip() +
  theme_minimal() +
  theme(
    panel.grid.major.y = element_line(linewidth = 0.2),
    panel.grid.minor.y = element_blank(),
    panel.grid.minor.x = element_blank(),
    panel.grid.major.x = element_blank(),
    axis.ticks = element_line(),
    axis.ticks.y = element_blank(),
    axis.ticks.length = unit(0.1, "cm")
  ) +
  labs(x = "Politician", y = "ICC") +
  figure_style +
  theme(axis.text.y = element_text(size = TEXT_PT))  # names are labels, not numbers

save_figure(p, "fig3_icc.pdf", height = 2.8)
