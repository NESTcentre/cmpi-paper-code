# Figure 2: daily CMPI for 12 European politicians in Russian-language media,
# January-December 2025. Panels are ordered by median CMPI (shown in each panel).

source("R/setup.R")

dat <- read_figshare("cmpi")

medians <- dat |>
  group_by(politician) |>
  summarise(m = median(cmpi) |> round(3)) |>
  arrange(-m)

dat <- dat |> mutate(politician = factor(politician, ordered = TRUE, levels = medians$politician))
medians <- medians |> mutate(politician = factor(politician, ordered = TRUE, levels = medians$politician))

p <- dat |>
  ggplot() +
  geom_hline(yintercept = 0, linewidth = 0.3, col = "grey80") +
  geom_line(aes(report_date, cmpi), linewidth = 0.18) +
  geom_text(
    data = medians,
    aes(x = as.Date(Inf), y = Inf, label = m),
    hjust = 1.3, vjust = 1.2,
    family = FONT, size = TICK_PT / .pt
  ) +
  facet_wrap(~politician, nrow = 4, scales = "free_y") +
  theme_minimal() +
  theme(
    axis.text.x.bottom = element_text(margin = margin(t = 1.5)),
    panel.grid.minor.y = element_blank(),
    panel.grid.major.y = element_line(colour = "gray90", linewidth = 0.2),
    panel.grid.minor.x = element_blank(),
    panel.grid.major.x = element_blank(),
    axis.ticks = element_line(),
    axis.ticks.y = element_blank(),
    axis.ticks.length = unit(0.1, "cm"),
    strip.text = element_text(face = "bold"),
    panel.spacing.x = unit(0.7, "lines"),
    panel.spacing.y = unit(1, "lines")
  ) +
  scale_x_date(
    limits = as.Date(c("2025-01-01", "2025-12-31")),
    breaks = seq(as.Date("2025-01-01"), as.Date("2025-12-01"), by = "1 month"),
    labels = function(x) substr(format(x, "%b"), 1, 1),
    expand = expansion(mult = c(0, 0))
  ) +
  aligned_y_axis(n_breaks = 3, expand = c(0.05, 0.25)) +  # headroom for the medians
  labs(x = "", y = "CMPI") +
  figure_style +
  theme(axis.ticks = element_line(linewidth = 0.2),  # lighter ticks for thin lines
        axis.ticks.length = unit(0.08, "cm"))

save_figure(p, "fig2_cmpi_timeseries.pdf", height = 4.4)
