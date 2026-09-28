import csv

from cmpi_simulation import aggregate


def _write_per_cell(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["replicate_index", "day_type", "algorithm", "parameter", "recovered_K", "ari", "cmpi_paper", "cmpi_alt"],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def test_aggregate_means_and_sds(tmp_path):
    in_path = tmp_path / "per_cell.csv"
    out_path = tmp_path / "results.csv"
    rows = []
    for r in range(3):
        rows.append({
            "replicate_index": r, "day_type": "low_cmpi", "algorithm": "lfa", "parameter": 0.7,
            "recovered_K": 10, "ari": 1.0, "cmpi_paper": 1.30 + r * 0.01, "cmpi_alt": 1.20 + r * 0.01,
        })
    _write_per_cell(in_path, rows)
    aggregate.aggregate(per_cell_path=in_path, out_path=out_path)
    out_rows = list(csv.DictReader(out_path.open()))
    assert len(out_rows) == 1
    out = out_rows[0]
    assert out["day_type"] == "low_cmpi"
    assert out["algorithm"] == "lfa"
    assert abs(float(out["cmpi_paper_mean"]) - 1.31) < 1e-9
    assert abs(float(out["cmpi_paper_sd"]) - 0.01) < 0.01
