# Reproduces all figures (written to output/) and prints all statistics quoted
# in the text. Run from this directory:  Rscript run_all.R

for (script in c("figure_1.R", "figure_2.R", "figure_3.R", "figure_4.R", "numbers.R")) {
  message("\n== ", script)
  source(script, local = new.env())
}
