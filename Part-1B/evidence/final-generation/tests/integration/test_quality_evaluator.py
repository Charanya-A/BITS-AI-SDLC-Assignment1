"""Tests for the classification-quality evaluator."""

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parents[2] / ".harness"
sys.path.insert(0, str(HARNESS_DIR))

from evaluate_quality import evaluate_quality, QUALITY_THRESHOLD


def test_quality_evaluation_blocks_when_data_gate_is_not_passed(tmp_path):
    result = evaluate_quality(
        manifest_path=tmp_path / "dataset.json",
        predictions={},
        data_gate_passed=False,
    )

    assert result["passed"] is False
    assert result["evaluation_dataset_valid"] is False
    assert result["metrics"]["macro_f1"] == 0
    assert result["failure_evidence"][0]["code"] == "DATA_GATE_NOT_PASSED"


def test_quality_threshold_is_fixed_at_point_eighty():
    assert QUALITY_THRESHOLD == 0.80


def test_quality_evaluation_blocks_when_manifest_is_missing(tmp_path):
    result = evaluate_quality(
        manifest_path=tmp_path / "missing.json",
        predictions={},
        data_gate_passed=True,
    )

    assert result["passed"] is False
    assert result["evaluation_dataset_valid"] is False
    assert any(
        failure["code"] == "EVALUATION_DATASET_INVALID"
        for failure in result["failure_evidence"]
    )