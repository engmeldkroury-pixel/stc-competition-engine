from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Mapping, Sequence


NumberRow = Mapping[str, float | int]


@dataclass(frozen=True)
class CorrelationAudit:
    features: tuple[str, ...]
    pearson: tuple[tuple[float, ...], ...]
    spearman: tuple[tuple[float, ...], ...]
    effective_rank: float
    sample_size: int


@dataclass(frozen=True)
class PCAFit:
    features: tuple[str, ...]
    means: tuple[float, ...]
    scales: tuple[float, ...]
    eigenvalues: tuple[float, ...]
    components: tuple[tuple[float, ...], ...]
    explained_variance_ratio: tuple[float, ...]
    sample_size: int


def _matrix(rows: Iterable[NumberRow], features: Sequence[str]) -> list[list[float]]:
    names = tuple(features)
    if not names:
        raise ValueError("features must not be empty")
    out: list[list[float]] = []
    for row in rows:
        vals: list[float] = []
        missing = False
        for name in names:
            raw = row.get(name)
            if raw is None:
                missing = True
                break
            try:
                value = float(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"non-numeric feature {name}") from exc
            if value != value or value in (float("inf"), float("-inf")):
                missing = True
                break
            vals.append(value)
        if not missing:
            out.append(vals)
    if len(out) < 3:
        raise ValueError("at least three complete rows are required")
    return out


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _sample_std(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    return sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))


def _pearson(x: Sequence[float], y: Sequence[float]) -> float:
    mx, my = _mean(x), _mean(y)
    sx = sum((v - mx) ** 2 for v in x)
    sy = sum((v - my) ** 2 for v in y)
    if sx <= 0.0 or sy <= 0.0:
        return 0.0
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return max(-1.0, min(1.0, cov / sqrt(sx * sy)))


def _average_ranks(values: Sequence[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def _correlation_matrix(matrix: Sequence[Sequence[float]], *, rank: bool) -> list[list[float]]:
    cols = [list(col) for col in zip(*matrix)]
    if rank:
        cols = [_average_ranks(col) for col in cols]
    n = len(cols)
    return [
        [1.0 if i == j else _pearson(cols[i], cols[j]) for j in range(n)]
        for i in range(n)
    ]


def effective_rank_from_correlation(corr: Sequence[Sequence[float]]) -> float:
    """Participation-ratio effective rank without an eigensolver.

    For a correlation matrix, sum(eigenvalues)=trace=p and
    sum(eigenvalues^2)=trace(C^2)=sum(C_ij^2).
    """
    p = len(corr)
    if p == 0 or any(len(row) != p for row in corr):
        raise ValueError("correlation matrix must be square and non-empty")
    denom = sum(float(v) ** 2 for row in corr for v in row)
    if denom <= 0.0:
        return 0.0
    return (float(p) * float(p)) / denom


def correlation_audit(rows: Iterable[NumberRow], features: Sequence[str]) -> CorrelationAudit:
    names = tuple(features)
    m = _matrix(rows, names)
    pearson = _correlation_matrix(m, rank=False)
    spearman = _correlation_matrix(m, rank=True)
    return CorrelationAudit(
        features=names,
        pearson=tuple(tuple(v for v in row) for row in pearson),
        spearman=tuple(tuple(v for v in row) for row in spearman),
        effective_rank=effective_rank_from_correlation(pearson),
        sample_size=len(m),
    )


def _standardize(matrix: Sequence[Sequence[float]]) -> tuple[list[list[float]], list[float], list[float]]:
    cols = [list(col) for col in zip(*matrix)]
    means = [_mean(col) for col in cols]
    scales = [_sample_std(col) for col in cols]
    safe_scales = [s if s > 1e-12 else 1.0 for s in scales]
    standardized = [
        [(row[j] - means[j]) / safe_scales[j] for j in range(len(means))]
        for row in matrix
    ]
    return standardized, means, safe_scales


def _covariance(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    n = len(matrix)
    p = len(matrix[0])
    if n < 2:
        raise ValueError("at least two rows are required")
    return [
        [
            sum(matrix[i][a] * matrix[i][b] for i in range(n)) / (n - 1)
            for b in range(p)
        ]
        for a in range(p)
    ]


def _jacobi_eigh(
    matrix: Sequence[Sequence[float]],
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 20000,
) -> tuple[list[float], list[list[float]]]:
    """Pure-Python symmetric eigendecomposition for small research matrices."""
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square and non-empty")
    a = [[float(v) for v in row] for row in matrix]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for _ in range(max_iterations):
        p = q = 0
        largest = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                av = abs(a[i][j])
                if av > largest:
                    largest, p, q = av, i, j
        if largest <= tolerance:
            break

        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        tau = (aqq - app) / (2.0 * apq)
        t = (1.0 if tau >= 0 else -1.0) / (abs(tau) + sqrt(1.0 + tau * tau))
        c = 1.0 / sqrt(1.0 + t * t)
        s = t * c

        for k in range(n):
            if k in (p, q):
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = c * akp - s * akq
            a[k][q] = a[q][k] = s * akp + c * akq

        a[p][p] = app - t * apq
        a[q][q] = aqq + t * apq
        a[p][q] = a[q][p] = 0.0

        for k in range(n):
            vkp, vkq = v[k][p], v[k][q]
            v[k][p] = c * vkp - s * vkq
            v[k][q] = s * vkp + c * vkq
    else:
        raise RuntimeError("Jacobi eigensolver did not converge")

    eigenvalues = [a[i][i] for i in range(n)]
    eigenvectors = [[v[row][col] for row in range(n)] for col in range(n)]
    pairs = sorted(zip(eigenvalues, eigenvectors), key=lambda item: item[0], reverse=True)
    return [max(0.0, x) for x, _ in pairs], [vec for _, vec in pairs]


def fit_pca_training_only(
    training_rows: Iterable[NumberRow],
    features: Sequence[str],
) -> PCAFit:
    """Fit PCA on the training fold only.

    Holdout rows are intentionally absent from this API so they cannot influence
    scaling or components by accident.
    """
    names = tuple(features)
    m = _matrix(training_rows, names)
    standardized, means, scales = _standardize(m)
    cov = _covariance(standardized)
    eigenvalues, components = _jacobi_eigh(cov)
    total = sum(eigenvalues)
    ratios = [0.0 if total <= 0.0 else value / total for value in eigenvalues]
    return PCAFit(
        features=names,
        means=tuple(means),
        scales=tuple(scales),
        eigenvalues=tuple(eigenvalues),
        components=tuple(tuple(v for v in component) for component in components),
        explained_variance_ratio=tuple(ratios),
        sample_size=len(m),
    )


def transform_pca(rows: Iterable[NumberRow], fit: PCAFit, n_components: int | None = None) -> list[list[float]]:
    names = fit.features
    m = _matrix(rows, names)
    k = len(fit.components) if n_components is None else max(1, min(int(n_components), len(fit.components)))
    out: list[list[float]] = []
    for row in m:
        z = [(row[j] - fit.means[j]) / fit.scales[j] for j in range(len(names))]
        out.append([
            sum(z[j] * fit.components[i][j] for j in range(len(names)))
            for i in range(k)
        ])
    return out


def stratify_rows(rows: Iterable[Mapping[str, object]], keys: Sequence[str]) -> dict[tuple[object, ...], list[Mapping[str, object]]]:
    if not keys:
        raise ValueError("at least one stratification key is required")
    out: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
    for row in rows:
        key = tuple(row.get(name) for name in keys)
        out.setdefault(key, []).append(row)
    return out


def paired_outcome_delta(
    baseline: Mapping[str, float],
    candidate: Mapping[str, float],
) -> dict[str, float | int]:
    """Compare synchronized OOS outcomes by immutable candidate/session id."""
    common = sorted(set(baseline) & set(candidate))
    if not common:
        raise ValueError("no paired outcomes")
    deltas = [float(candidate[k]) - float(baseline[k]) for k in common]
    return {
        "pairs": len(common),
        "mean_delta": _mean(deltas),
        "positive_pairs": sum(x > 0 for x in deltas),
        "negative_pairs": sum(x < 0 for x in deltas),
        "zero_pairs": sum(x == 0 for x in deltas),
    }
