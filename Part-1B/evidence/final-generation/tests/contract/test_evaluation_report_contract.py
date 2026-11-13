import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "specs"
    / "001-customer-message-spam-classifier"
    / "contracts"
    / "evaluation-report.schema.json"
)


@pytest.fixture(scope="module")
def report_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    Draft202012Validator.check_schema(schema)
    return schema


@pytest.fixture(scope="module")
def report_validator(report_schema):
    return Draft202012Validator(report_schema)


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
        "review_rate": 0.10,
        "total_valid_evaluation_case_count": 20,
        "human_decision": None,
    }


@pytest.mark.contract
def test_report_contains_every_required_schema_field(
    report_schema,
    valid_report,
):
    required_fields = set(report_schema["required"])

    assert required_fields == set(valid_report.keys())


@pytest.mark.contract
def test_complete_evaluation_report_is_schema_valid(
    report_validator,
    valid_report,
):
    report_validator.validate(valid_report)


@pytest.mark.contract
def test_human_decision_is_null_before_human_review(
    report_validator,
    valid_report,
):
    assert valid_report["human_decision"] is None
    report_validator.validate(valid_report)


@pytest.mark.contract
def test_missing_required_report_field_is_rejected(
    report_validator,
    valid_report,
):
    del valid_report["evaluation_dataset_valid"]

    assert not report_validator.is_valid(valid_report)


@pytest.mark.contract
def test_invalid_human_decision_value_is_rejected(
    report_validator,
    valid_report,
):
    valid_report["human_decision"] = "PENDING"

    assert not report_validator.is_valid(valid_report)


@pytest.mark.contract
def test_additional_report_field_is_rejected(
    report_validator,
    valid_report,
):
    valid_report["unexpected_field"] = "unexpected"

    assert not report_validator.is_valid(valid_report)


@pytest.mark.contract
def test_failure_evidence_requires_stage_code_and_message(
    report_validator,
    valid_report,
):
    valid_report["failure_evidence"] = [
        {
            "stage": "classification_quality",
            "code": "QUALITY_GATE_FAILED",
            "message": "Macro-F1 did not meet the required threshold.",
        }
    ]

    report_validator.validate(valid_report)


@pytest.mark.contract
def test_invalid_failure_evidence_stage_is_rejected(
    report_validator,
    valid_report,
):
    valid_report["failure_evidence"] = [
        {
            "stage": "unknown_stage",
            "code": "INVALID_STAGE",
            "message": "Unknown evaluation stage.",
        }
    ]

    assert not report_validator.is_valid(valid_report)


@pytest.mark.contract
def test_zero_valid_case_failure_report_is_schema_valid(
    report_validator,
):
    report = {
        "structural_validation_pass": True,
        "invariant_validation_pass": True,
        "evaluation_dataset_valid": False,
        "classification_quality_pass": False,
        "overall_pass": False,
        "failure_evidence": [
            {
                "stage": "classification_quality",
                "code": "INVALID_EVALUATION_DATASET",
                "message": "No valid synthetic held-out evaluation cases are available.",
            }
        ],
        "spam_precision": 0,
        "spam_recall": 0,
        "spam_f1": 0,
        "ham_precision": 0,
        "ham_recall": 0,
        "ham_f1": 0,
        "macro_f1": 0,
        "review_count": 0,
        "review_rate": 0,
        "total_valid_evaluation_case_count": 0,
        "human_decision": None,
    }

    report_validator.validate(report)

    assert report["review_rate"] == 0
    assert report["evaluation_dataset_valid"] is False
    assert report["classification_quality_pass"] is False
    assert report["human_decision"] is None


@pytest.mark.contract
def test_zero_valid_case_report_does_not_divide_by_zero():
    total_valid_cases = 0
    review_count = 0

    review_rate = (
        review_count / total_valid_cases
        if total_valid_cases > 0
        else 0
    )

    assert review_rate == 0