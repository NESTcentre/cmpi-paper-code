# Figure 4: daily CMPI against the simple proportion of mentions, with
# Chatterjee's xi coefficient (XICOR::calculateXI) in each panel title.
# Panels are ordered by median CMPI.

source("R/setup.R")

cmpi <- read_figshare("cmpi")
props <- read_figshare("proportions")

# Days on which both measures are available (CMPI covers each politician's
# time in office; the proportions cover all of 2025).
dat <- inner_join(cmpi, props, by = c("politician", "report_date"))

panel_order <- dat |>
  group_by(politician) |>
  summarise(m = median(cmpi)) |>
  arrange(-m) |>
  pull(politician)

# calculateXI() breaks ties in x at random (zero-mention days tie), which can
# change the third decimal, so the seed is fixed.
set.seed(2026)
xi <- dat |>
  group_by(politician) |>
  summarise(xi = suppressWarnings(XICOR::calculateXI(proportion, cmpi)), .groups = "drop")

labels <- xi |> mutate(label = sprintf("%s\nξ = %.3f", politician, xi))

dat <- dat |>
  left_join(labels, by = "politician") |>
  mutate(label = factor(label, levels = labels$label[match(panel_order, labels$politician)]))

p <- dat |>
  ggplot(aes(proportion, cmpi)) +
  geom_point(alpha = 0.2, size = 0.8, shape = 16) +
  facet_wrap(~label, scales = "free") +
  aligned_y_axis(n_breaks = 4, expand = c(0.04, 0.04)) +
  scale_x_continuous(n.breaks = 3) +
  theme_minimal() +
  theme(
    panel.grid.minor.y = element_blank(),
    panel.grid.major.y = element_line(colour = "gray90", linewidth = 0.2),
    panel.grid.minor.x = element_blank(),
    panel.grid.major.x = element_blank(),
    axis.ticks = element_line(),
    axis.ticks.y = element_blank(),
    axis.ticks.length = unit(0.1, "cm"),
    strip.text = element_text(face = "bold", lineheight = 1.1),
    panel.spacing.x = unit(0.7, "lines"),
    panel.spacing.y = unit(0.8, "lines")
  ) +
  labs(x = "Simple proportion of mentions (%)", y = "CMPI") +
  figure_style

save_figure(p, "fig4_cmpi_vs_proportion.pdf", height = 3.9)
