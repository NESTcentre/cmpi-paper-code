"""CMPI computation.

CMPI(e) = (1 / log(N + 1)) * sum_k S(e, G_k) * log(n_k + 1).
"""

import math


def compute_cmpi(clusters: list[dict], *, total_n: int) -> float:
    """Compute CMPI from a list of cluster dicts and the total document count.

    Each cluster dict must carry:
        - size: int (n_k)
        - salience: float (S(e, G_k); typically in [0, 1] but the formula tolerates any non-negative value)
    """
    if total_n <= 0:
        return 0.0
    numerator = sum(c["salience"] * math.log(c["size"] + 1) for c in clusters)
    return numerator / math.log(total_n + 1)
