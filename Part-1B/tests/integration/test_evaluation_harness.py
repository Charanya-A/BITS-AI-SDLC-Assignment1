import json

import pytest

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parents[2] / ".harness"
sys.path.insert(0, str(HARNESS_DIR))

from run_evaluation import run_pipeline


def stage_result(passed=True, failure_evidence=None):
    return {
        "passed": passed,
        "failure_evidence": failure_evidence or [],
    }


def quality_result(passed=True, dataset_valid=True):
    return {
        "passed": passed,
        "evaluation_dataset_valid": dataset_valid,
        "metrics": {
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
        },
        "failure_evidence": [],
    }


@pytest.mark.integration
def test_all_evaluation_stages_are_reported_independently(tmp_path):
    report = run_pipeline(
        structural_stage=lambda: stage_result(),
        invariant_stage=lambda: stage_result(),
        quality_stage=lambda: quality_result(),
        output_path=tmp_path / "eval-results.json",
    )

    assert report["structural_validation_pass"] is True
    assert report["invariant_validation_pass"] is True
    assert report["classification_quality_pass"] is True
    assert report["evaluation_dataset_valid"] is True
    assert report["overall_pass"] is True


@pytest.mark.integration
@pytest.mark.parametrize(
    ("failed_stage", "expected_fields"),
    [
        (
            "structural",
            {
                "structural_validation_pass": False,
                "invariant_validation_pass": True,
                "classification_quality_pass": True,
            },
        ),
        (
            "invariant",
            {
                "structural_validation_pass": True,
                "invariant_validation_pass": False,
                "classification_quality_pass": True,
            },
        ),
        (
            "quality",
            {
                "structural_validation_pass": True,
                "invariant_validation_pass": True,
                "classification_quality_pass": False,
            },
        ),
    ],
)
def test_stage_failure_is_reported_without_hiding_other_outcomes(
    tmp_path,
    failed_stage,
    expected_fields,
):
    structural = stage_result(passed=failed_stage != "structural")
    invariant = stage_result(passed=failed_stage != "invariant")
    quality = quality_result(passed=failed_stage != "quality")

    report = run_pipeline(
        structural_stage=lambda: structural,
        invariant_stage=lambda: invariant,
        quality_stage=lambda: quality,
        output_path=tmp_path / "eval-results.json",
    )

    for field, expected in expected_fields.items():
        assert report[field] is expected

    assert report["overall_pass"] is False


@pytest.mark.integration
def test_automated_evaluation_never_assigns_human_decision(tmp_path):
    report = run_pipeline(
        structural_stage=lambda: stage_result(),
        invariant_stage=lambda: stage_result(),
        quality_stage=lambda: quality_result(),
        output_path=tmp_path / "eval-results.json",
    )

    assert report["human_decision"] is None

    saved_report = json.loads(
        (tmp_path / "eval-results.json").read_text(encoding="utf-8")
    )
    assert saved_report["human_decision"] is None


@pytest.mark.integration
def test_all_stages_run_even_when_structural_validation_fails(tmp_path):
    calls = []

    def structural():
        calls.append("structural")
        return stage_result(passed=False)

    def invariant():
        calls.append("invariant")
        return stage_result()

    def quality():
        calls.append("quality")
        return quality_result()

    run_pipeline(
        structural_stage=structural,
        invariant_stage=invariant,
        quality_stage=quality,
        output_path=tmp_path / "eval-results.json",
    )

    assert calls == ["structural", "invariant", "quality"]
