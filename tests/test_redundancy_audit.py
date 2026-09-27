from __future__ import annotations

import math

from research_tools.redundancy_audit import (
    correlation_audit,
    effective_rank_from_correlation,
    fit_pca_training_only,
    paired_outcome_delta,
    stratify_rows,
    transform_pca,
)


def test_effective_rank_detects_duplicate_information():
    independent = [[1.0, 0.0], [0.0, 1.0]]
    duplicate = [[1.0, 1.0], [1.0, 1.0]]
    assert effective_rank_from_correlation(independent) == 2.0
    assert effective_rank_from_correlation(duplicate) == 1.0


def test_correlation_audit_reports_perfect_duplicate_feature():
    rows = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 2, "b": 4, "c": 1},
        {"a": 3, "b": 6, "c": 4},
        {"a": 4, "b": 8, "c": 2},
    ]
    audit = correlation_audit(rows, ["a", "b", "c"])
    assert audit.sample_size == 4
    assert math.isclose(audit.pearson[0][1], 1.0, abs_tol=1e-12)
    assert math.isclose(audit.spearman[0][1], 1.0, abs_tol=1e-12)
    assert audit.effective_rank < 3.0


def test_pca_is_fit_only_from_training_rows():
    train = [
        {"a": 1, "b": 1},
        {"a": 2, "b": 2},
        {"a": 3, "b": 3},
        {"a": 4, "b": 4},
    ]
    fit = fit_pca_training_only(train, ["a", "b"])
    holdout_a = [{"a": 5, "b": 5}, {"a": 6, "b": 6}, {"a": 7, "b": 7}]
    holdout_b = [{"a": 5000, "b": -9000}, {"a": -2000, "b": 8000}, {"a": 4, "b": 99}]
    assert fit.means == (2.5, 2.5)
    assert fit.sample_size == 4

    transformed_a = transform_pca(holdout_a, fit, n_components=1)
    transformed_b = transform_pca(holdout_b, fit, n_components=1)
    assert transformed_a != transformed_b
    # The fit itself is unchanged because no holdout data enters fit_pca_training_only.
    assert fit.means == (2.5, 2.5)
    assert math.isclose(sum(fit.explained_variance_ratio), 1.0, abs_tol=1e-9)


def test_stratification_and_paired_outcome_delta_are_deterministic():
    rows = [
        {"asset_class": "index", "side": "LONG", "x": 1},
        {"asset_class": "index", "side": "SHORT", "x": 2},
        {"asset_class": "fx", "side": "LONG", "x": 3},
    ]
    grouped = stratify_rows(rows, ["asset_class", "side"])
    assert len(grouped[("index", "LONG")]) == 1
    assert len(grouped[("index", "SHORT")]) == 1
    assert len(grouped[("fx", "LONG")]) == 1

    delta = paired_outcome_delta(
        {"a": 1.0, "b": -1.0, "c": 0.2},
        {"a": 1.2, "b": -0.8, "c": 0.2},
    )
    assert delta["pairs"] == 3
    assert math.isclose(float(delta["mean_delta"]), (0.2 + 0.2 + 0.0) / 3.0, abs_tol=1e-12)
    assert delta["positive_pairs"] == 2
    assert delta["zero_pairs"] == 1
