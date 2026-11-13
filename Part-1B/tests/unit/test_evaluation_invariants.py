import copy

import pytest

from spam_classifier.evaluation import validate_report_invariants


@pytest.fixture
def valid_report():
    return {
        "structural_validation_pass": True,
        "invariant_validation_pass": True,
        "evaluation_dataset_valid": True,
        "classification_quality_pass": True,
        "overall_pass": True,
        "failure_evidence": [],
        "spam_precision": 0.90,
        "spam_recall": 0.85,
        "spam_f1": 0.8743,
        "ham_precision": 0.88,
        "ham_recall": 0.90,
        "ham_f1": 0.8894,
        "macro_f1": (0.8743 + 0.8894) / 2,
        "review_count": 2,
        "review_rate": 2 / 20,
        "total_valid_evaluation_case_count": 20,
        "human_decision": None,
    }


@pytest.mark.unit
def test_valid_report_satisfies_all_invariants(valid_report):
    assert validate_report_invariants(valid_report) is True


@pytest.mark.unit
def test_review_count_cannot_exceed_total_valid_case_count(valid_report):
    report = copy.deepcopy(valid_report)
    report["review_count"] = 21

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_review_rate_must_match_review_count_and_total(valid_report):
    report = copy.deepcopy(valid_report)
    report["review_rate"] = 0.50

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_zero_case_report_requires_zero_review_rate(valid_report):
    report = copy.deepcopy(valid_report)
    report["review_count"] = 0
    report["review_rate"] = 0
    report["total_valid_evaluation_case_count"] = 0
    report["spam_precision"] = 0
    report["spam_recall"] = 0
    report["spam_f1"] = 0
    report["ham_precision"] = 0
    report["ham_recall"] = 0
    report["ham_f1"] = 0
    report["macro_f1"] = 0
    report["evaluation_dataset_valid"] = False
    report["classification_quality_pass"] = False
    report["overall_pass"] = False

    assert validate_report_invariants(report) is True


@pytest.mark.unit
def test_zero_case_report_with_nonzero_review_rate_is_invalid(valid_report):
    report = copy.deepcopy(valid_report)
    report["review_count"] = 0
    report["review_rate"] = 0.1
    report["total_valid_evaluation_case_count"] = 0
    report["evaluation_dataset_valid"] = False
    report["classification_quality_pass"] = False
    report["overall_pass"] = False

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_macro_f1_must_equal_mean_of_spam_and_ham_f1(valid_report):
    report = copy.deepcopy(valid_report)
    report["macro_f1"] = 0.95

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_invalid_dataset_cannot_pass_classification_quality(valid_report):
    report = copy.deepcopy(valid_report)
    report["evaluation_dataset_valid"] = False
    report["classification_quality_pass"] = True
    report["overall_pass"] = False

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_macro_f1_below_threshold_cannot_pass_quality_gate(valid_report):
    report = copy.deepcopy(valid_report)
    report["spam_f1"] = 0.70
    report["ham_f1"] = 0.70
    report["macro_f1"] = 0.70
    report["classification_quality_pass"] = True
    report["overall_pass"] = True

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_valid_dataset_with_macro_f1_at_threshold_can_pass_quality(valid_report):
    report = copy.deepcopy(valid_report)
    report["spam_f1"] = 0.80
    report["ham_f1"] = 0.80
    report["macro_f1"] = 0.80

    assert validate_report_invariants(report) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "failed_field",
    [
        "structural_validation_pass",
        "invariant_validation_pass",
        "evaluation_dataset_valid",
        "classification_quality_pass",
    ],
)
def test_overall_pass_requires_every_stage_and_quality_gate(
    valid_report,
    failed_field,
):
    report = copy.deepcopy(valid_report)
    report[failed_field] = False
    report["overall_pass"] = True

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_overall_pass_must_be_false_when_a_required_stage_fails(valid_report):
    report = copy.deepcopy(valid_report)
    report["structural_validation_pass"] = False
    report["overall_pass"] = False

    assert validate_report_invariants(report) is True


@pytest.mark.unit
def test_automated_evaluation_must_not_assign_human_decision(valid_report):
    report = copy.deepcopy(valid_report)
    report["human_decision"] = "ACCEPT"

    assert validate_report_invariants(report) is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -0.01,
        1.01,
        True,
        "0.90",
        None,
    ],
)
def test_invalid_metric_values_are_rejected(valid_report, invalid_value):
    report = copy.deepcopy(valid_report)
    report["spam_precision"] = invalid_value

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_boolean_review_count_is_rejected(valid_report):
    report = copy.deepcopy(valid_report)
    report["review_count"] = True

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_boolean_total_case_count_is_rejected(valid_report):
    report = copy.deepcopy(valid_report)
    report["total_valid_evaluation_case_count"] = True

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_non_list_failure_evidence_is_rejected(valid_report):
    report = copy.deepcopy(valid_report)
    report["failure_evidence"] = "no failures"

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_missing_required_report_field_is_rejected(valid_report):
    report = copy.deepcopy(valid_report)
    del report["macro_f1"]

    assert validate_report_invariants(report) is False


@pytest.mark.unit
def test_non_boolean_stage_result_is_rejected(valid_report):
    report = copy.deepcopy(valid_report)
    report["structural_validation_pass"] = 1

    assert validate_report_invariants(report) is False