"""Deterministic global alignment (Needleman–Wunsch, minimum cost). E002-04, E002-07."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from .lexicon import SILENT_R
from .markers import substitution_cost

GAP = 1.2
Pair = tuple[int | None, int | None]  # (target index, observed index)


def _target_gap_cost(target: str) -> float:
    # Silently dropping a non-rhotic (r) is exactly what SSBE does: free.
    return 0.0 if target == SILENT_R else GAP


def align(
    target: Sequence[str],
    observed: Sequence[str],
    sub: Callable[[str, str], float] = substitution_cost,
) -> list[Pair]:
    """Return aligned index pairs. Ties break diag > delete(target) > insert(observed)."""
    n, m = len(target), len(observed)
    inf = float("inf")
    cost = [[inf] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]  # 0 diag, 1 up (target gap in obs), 2 left
    cost[0][0] = 0.0
    for i in range(1, n + 1):
        cost[i][0] = cost[i - 1][0] + _target_gap_cost(target[i - 1])
        back[i][0] = 1
    for j in range(1, m + 1):
        cost[0][j] = cost[0][j - 1] + GAP
        back[0][j] = 2

    for i in range(1, n + 1):
        t = target[i - 1]
        tg = _target_gap_cost(t)
        for j in range(1, m + 1):
            d = cost[i - 1][j - 1] + sub(t, observed[j - 1])
            u = cost[i - 1][j] + tg
            l = cost[i][j - 1] + GAP
            # Round to avoid float-noise-dependent tie breaking (determinism, E002-07).
            d, u, l = round(d, 6), round(u, 6), round(l, 6)
            if d <= u and d <= l:
                cost[i][j], back[i][j] = d, 0
            elif u <= l:
                cost[i][j], back[i][j] = u, 1
            else:
                cost[i][j], back[i][j] = l, 2

    pairs: list[Pair] = []
    i, j = n, m
    while i > 0 or j > 0:
        b = back[i][j]
        if i > 0 and j > 0 and b == 0:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif i > 0 and (j == 0 or b == 1):
            pairs.append((i - 1, None))
            i -= 1
        else:
            pairs.append((None, j - 1))
            j -= 1
    pairs.reverse()
    return pairs
