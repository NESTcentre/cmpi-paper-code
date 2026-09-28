# Figure 1: theoretical upper bound of CMPI as a function of corpus size N
# for different numbers of contextual clusters K (uniform cluster sizes).
# No data needed.

source("R/setup.R")

cmpi_max <- function(K, N) {
  K * log(N / K + 1) / log(N + 1)
}

N <- seq(1, 10000, length.out = 200)
df <- bind_rows(lapply(c(10, 100, 500, 1000), function(k) {
  tibble::tibble(K = as.factor(k), N = N, CMPI = cmpi_max(k, N))
}))

p <- df |>
  ggplot(aes(N, CMPI, linetype = K)) +
  geom_line(linewidth = 0.35) +
  scale_linetype_manual(values = c("solid", "dashed", "dotted", "dotdash", "longdash")) +
  geom_hline(yintercept = 0, linewidth = 0.3, col = "grey") +
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
  ylim(c(0, 300)) +
  figure_style

save_figure(p, "fig1_upper_bound.pdf", height = 2.3)
