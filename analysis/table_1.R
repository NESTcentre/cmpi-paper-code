# Table 1: CMPI under a fixed overall proportion of mentioning documents
# (N = 1000 documents, M = 200 of which mention the entity), for three
# allocations of the mentions across contextual clusters.
# CMPI(e) = sum_k S(e, G_k) * log(n_k + 1) / log(N + 1), with S = m_k / n_k.
# No data needed.

cmpi <- function(n, m) sum((m / n) * log(n + 1)) / log(sum(n) + 1)

scenarios <- list(
  # one cluster of 500 holding all 200 mentions; 500 documents in 9 clusters
  # without mentions (their sizes do not affect CMPI, as their salience is 0)
  Low      = list(n = c(500, rep(56, 8), 52), m = c(200, rep(0, 9))),
  # 10 clusters of 100; 40 mentions in each of 5 of them
  Moderate = list(n = rep(100, 10), m = c(rep(40, 5), rep(0, 5))),
  # 20 clusters of 20 with 10 mentions each; the remaining 600 documents in one cluster
  High     = list(n = c(rep(20, 20), 600), m = c(rep(10, 20), 0))
)

table_1 <- data.frame(
  spread = names(scenarios),
  N = sapply(scenarios, function(s) sum(s$n)),
  M = sapply(scenarios, function(s) sum(s$m)),
  simple_proportion = sapply(scenarios, function(s) sum(s$m) / sum(s$n)),
  CMPI = sapply(scenarios, function(s) round(cmpi(s$n, s$m), 2)),
  row.names = NULL
)

cat("\nTable 1\n")
print(table_1)
