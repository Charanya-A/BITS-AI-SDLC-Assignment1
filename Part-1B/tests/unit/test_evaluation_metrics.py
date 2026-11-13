import pytest

from spam_classifier.evaluation import (
    calculate_classification_metrics,
    validate_evaluation_manifest,
)


@pytest.fixture
def metric_cases():
    cases = []

    labels = [
        ("s1", "SPAM"),
        ("s2", "SPAM"),
        ("s3", "SPAM"),
        ("s4", "SPAM"),
        ("h1", "HAM"),
        ("h2", "HAM"),
        ("h3", "HAM"),
        ("h4", "HAM"),
    ]

    for case_id, label in labels:
        cases.append(
            {
                "case_id": case_id,
                "case_group": "synthetic_held_out",
                "scenario": "normal",
                "message": f"Artificial metric test message {case_id}.",
                "expected_label": label,
                "expected_error": None,
                "requirement_refs": ["FR-010", "SC-004"],
            }
        )

    # These cases must not contribute to classification metrics.
    cases.extend(
        [
            {
                "case_id": "controlled-1",
                "case_group": "synthetic_controlled",
                "scenario": "boundary",
                "message": "Artificial controlled test message.",
                "expected_label": "SPAM",
                "expected_error": None,
                "requirement_refs": ["FR-010", "SC-004"],
            },
            {
                "case_id": "validation-missing",
                "case_group": "validation_only",
                "scenario": "missing",
                "expected_label": None,
                "expected_error": "MESSAGE_REQUIRED",
                "requirement_refs": ["FR-006", "SC-003"],
            },
            {
                "case_id": "validation-malformed",
                "case_group": "validation_only",
                "scenario": "malformed",
                "message": 123,
                "expected_label": None,
                "expected_error": "MESSAGE_INVALID_TYPE",
                "requirement_refs": ["FR-006", "SC-003"],
            },
        ]
    )

    return cases


@pytest.fixture
def metric_predictions():
    return {
        "s1": "SPAM",
        "s2": "SPAM",
        "s3": "HAM",
        "s4": "REVIEW",
        "h1": "HAM",
        "h2": "HAM",
        "h3": "SPAM",
        "h4": "REVIEW",
    }


@pytest.mark.unit
def test_calculates_spam_and_ham_precision_recall_and_f1(
    metric_cases,
    metric_predictions,
):
    metrics = calculate_classification_metrics(
        metric_cases,
        metric_predictions,
    )

    expected_f1 = 4 / 7

    assert metrics["spam_precision"] == pytest.approx(2 / 3)
    assert metrics["spam_recall"] == pytest.approx(0.5)
    assert metrics["spam_f1"] == pytest.approx(expected_f1)

    assert metrics["ham_precision"] == pytest.approx(2 / 3)
    assert metrics["ham_recall"] == pytest.approx(0.5)
    assert metrics["ham_f1"] == pytest.approx(expected_f1)


@pytest.mark.unit
def test_macro_f1_is_arithmetic_mean_of_class_f1_values(
    metric_cases,
    metric_predictions,
):
    metrics = calculate_classification_metrics(
        metric_cases,
        metric_predictions,
    )

    expected_macro_f1 = (
        metrics["spam_f1"] + metrics["ham_f1"]
    ) / 2

    assert metrics["macro_f1"] == pytest.approx(expected_macro_f1)


@pytest.mark.unit
def test_review_count_and_rate_use_only_synthetic_held_out_cases(
    metric_cases,
    metric_predictions,
):
    metrics = calculate_classification_metrics(
        metric_cases,
        metric_predictions,
    )

    assert metrics["review_count"] == 2
    assert metrics["review_rate"] == pytest.approx(2 / 8)


@pytest.mark.unit
def test_total_valid_case_count_includes_only_synthetic_held_out_cases(
    metric_cases,
    metric_predictions,
):
    metrics = calculate_classification_metrics(
        metric_cases,
        metric_predictions,
    )

    assert metrics["total_valid_evaluation_case_count"] == 8


@pytest.mark.unit
def test_review_predictions_count_as_false_negatives_for_true_class(
    metric_cases,
    metric_predictions,
):
    metrics = calculate_classification_metrics(
        metric_cases,
        metric_predictions,
    )

    # Four true SPAM cases: two correct, one HAM, and one REVIEW.
    assert metrics["spam_recall"] == pytest.approx(2 / 4)

    # Four true HAM cases: two correct, one SPAM, and one REVIEW.
    assert metrics["ham_recall"] == pytest.approx(2 / 4)


@pytest.mark.unit
def test_zero_predicted_positive_precision_is_zero(metric_cases):
    predictions = {
        case["case_id"]: "HAM"
        for case in metric_cases
        if case["case_group"] == "synthetic_held_out"
    }

    metrics = calculate_classification_metrics(
        metric_cases,
        predictions,
    )

    assert metrics["spam_precision"] == 0
    assert metrics["ham_precision"] == pytest.approx(0.5)


@pytest.mark.unit
def test_zero_ground_truth_positive_recall_is_zero_and_dataset_invalid():
    cases = []

    # Artificial manifest with no true SPAM cases.
    for index in range(15):
        cases.append(
            {
                "case_id": f"all-ham-{index + 1:03d}",
                "case_group": "synthetic_held_out",
                "scenario": "normal",
                "message": f"Artificial HAM test message {index + 1}.",
                "expected_label": "HAM",
                "expected_error": None,
                "requirement_refs": ["FR-010", "SC-004"],
            }
        )

    cases.extend(
        [
            {
                "case_id": "controlled-boundary",
                "case_group": "synthetic_controlled",
                "scenario": "boundary",
                "message": "Artificial boundary test message.",
                "expected_label": "HAM",
                "expected_error": None,
                "requirement_refs": ["FR-010", "SC-004"],
            },
            {
                "case_id": "controlled-ambiguous",
                "case_group": "synthetic_controlled",
                "scenario": "ambiguous",
                "message": "Artificial ambiguous test message.",
                "expected_label": "HAM",
                "expected_error": None,
                "requirement_refs": ["FR-010", "SC-004"],
            },
            {
                "case_id": "controlled-adversarial",
                "case_group": "synthetic_controlled",
                "scenario": "adversarial",
                "message": "Artificial adversarial test message.",
                "expected_label": "HAM",
                "expected_error": None,
                "requirement_refs": ["FR-010", "SC-004"],
            },
            {
                "case_id": "validation-missing",
                "case_group": "validation_only",
                "scenario": "missing",
                "expected_label": None,
                "expected_error": "MESSAGE_REQUIRED",
                "requirement_refs": ["FR-006", "SC-003"],
            },
            {
                "case_id": "validation-malformed",
                "case_group": "validation_only",
                "scenario": "malformed",
                "message": 123,
                "expected_label": None,
                "expected_error": "MESSAGE_INVALID_TYPE",
                "requirement_refs": ["FR-006", "SC-003"],
            },
        ]
    )

    predictions = {
        case["case_id"]: "HAM"
        for case in cases
        if case["case_group"] == "synthetic_held_out"
    }

    metrics = calculate_classification_metrics(cases, predictions)

    assert metrics["spam_recall"] == 0
    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_zero_sum_precision_and_recall_produces_zero_f1(metric_cases):
    predictions = {
        "s1": "HAM",
        "s2": "HAM",
        "s3": "HAM",
        "s4": "HAM",
        "h1": "HAM",
        "h2": "HAM",
        "h3": "HAM",
        "h4": "HAM",
    }

    metrics = calculate_classification_metrics(
        metric_cases,
        predictions,
    )

    assert metrics["spam_precision"] == 0
    assert metrics["spam_recall"] == 0
    assert metrics["spam_f1"] == 0


@pytest.mark.unit
def test_rejects_extra_prediction_ids(metric_cases, metric_predictions):
    metric_predictions["unexpected-case"] = "SPAM"

    with pytest.raises(ValueError, match="Prediction IDs must exactly match"):
        calculate_classification_metrics(metric_cases, metric_predictions)


@pytest.mark.unit
def test_rejects_missing_prediction_ids(metric_cases, metric_predictions):
    metric_predictions.pop("s1")

    with pytest.raises(ValueError, match="Prediction IDs must exactly match"):
        calculate_classification_metrics(metric_cases, metric_predictions)


@pytest.mark.unit
def test_controlled_and_validation_cases_do_not_affect_metrics(
    metric_cases,
    metric_predictions,
):
    baseline = calculate_classification_metrics(
        metric_cases,
        metric_predictions,
    )

    extra_cases = [
        {
            "case_id": "another-controlled",
            "case_group": "synthetic_controlled",
            "scenario": "adversarial",
            "message": "Another artificial controlled message.",
            "expected_label": "SPAM",
            "expected_error": None,
            "requirement_refs": ["FR-010", "SC-004"],
        }
    ]

    extended_cases = metric_cases + extra_cases

    unchanged = calculate_classification_metrics(
        extended_cases,
        metric_predictions,
    )

    assert unchanged == baseline


@pytest.mark.unit
def test_rejects_invalid_prediction_label(metric_cases, metric_predictions):
    metric_predictions["s1"] = "UNKNOWN"

    with pytest.raises(ValueError, match="Invalid classification prediction"):
        calculate_classification_metrics(metric_cases, metric_predictions)