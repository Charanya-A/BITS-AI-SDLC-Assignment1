import json
import sys
from pathlib import Path

import pytest

HARNESS_DIR = Path(__file__).resolve().parents[2] / ".harness"
sys.path.insert(0, str(HARNESS_DIR))

from validate_invariants import validate_invariants


@pytest.fixture
def valid_manifest(tmp_path):
    cases = []

    for index in range(15):
        cases.append({
            "case_id": f"artificial-{index + 1:03d}",
            "case_group": "synthetic_held_out",
            "scenario": "normal",
            "message": f"Artificial test message {index + 1}.",
            "expected_label": "SPAM" if index < 8 else "HAM",
            "expected_error": None,
            "requirement_refs": ["FR-010", "SC-004"],
        })

    for scenario in ("boundary", "ambiguous", "adversarial"):
        cases.append({
            "case_id": f"synthetic-{scenario}",
            "case_group": "synthetic_controlled",
            "scenario": scenario,
            "message": f"Artificial {scenario} test message.",
            "expected_label": "HAM",
            "expected_error": None,
            "requirement_refs": ["FR-010", "SC-004"],
        })

    cases.extend([
        {
            "case_id": "missing",
            "case_group": "validation_only",
            "scenario": "missing",
            "expected_label": None,
            "expected_error": "MESSAGE_REQUIRED",
            "requirement_refs": ["FR-006", "SC-003"],
        },
        {
            "case_id": "malformed",
            "case_group": "validation_only",
            "scenario": "malformed",
            "message": 123,
            "expected_label": None,
            "expected_error": "MESSAGE_INVALID_TYPE",
            "requirement_refs": ["FR-006", "SC-003"],
        },
    ])

    path = tmp_path / "dataset.json"
    path.write_text(json.dumps({"cases": cases}), encoding="utf-8")
    return path


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
        "review_rate": 2 / 15,
        "total_valid_evaluation_case_count": 15,
        "human_decision": None,
    }


@pytest.mark.unit
def test_valid_manifest_and_matching_report_pass(
    valid_manifest, valid_report
):
    result = validate_invariants(valid_report, valid_manifest)

    assert result["passed"] is True
    assert result["evaluation_dataset_valid"] is True
    assert result["failure_evidence"] == []


@pytest.mark.unit
def test_report_dataset_validity_mismatch_is_rejected(
    valid_manifest, valid_report
):
    valid_report["evaluation_dataset_valid"] = False

    result = validate_invariants(valid_report, valid_manifest)

    assert result["passed"] is False
    assert any(
        item["code"] == "DATASET_VALIDITY_MISMATCH"
        for item in result["failure_evidence"]
    )


@pytest.mark.unit
def test_invalid_manifest_cannot_be_reported_as_valid(
    tmp_path, valid_report
):
    missing_manifest = tmp_path / "missing.json"

    result = validate_invariants(valid_report, missing_manifest)

    assert result["passed"] is False
    assert result["evaluation_dataset_valid"] is False
    assert any(
        item["code"] == "DATASET_VALIDITY_MISMATCH"
        for item in result["failure_evidence"]
    )


@pytest.mark.unit
def test_human_decision_must_remain_null(
    valid_manifest, valid_report
):
    valid_report["human_decision"] = "ACCEPT"

    result = validate_invariants(valid_report, valid_manifest)

    assert result["passed"] is False
    assert any(
        item["code"] == "HUMAN_DECISION_NOT_NULL"
        for item in result["failure_evidence"]
    )


@pytest.mark.unit
def test_non_object_report_is_rejected(valid_manifest):
    result = validate_invariants(None, valid_manifest)

    assert result["passed"] is False
    assert any(
        item["code"] == "REPORT_INVALID"
        for item in result["failure_evidence"]
    )