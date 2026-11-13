"""Classification-quality evaluation for eligible held-out cases."""

import json

from spam_classifier.evaluation import (
    calculate_classification_metrics,
    load_evaluation_manifest,
    select_quality_cases,
    validate_evaluation_manifest,
)

QUALITY_THRESHOLD = 0.80


def evaluate_quality(
    manifest_path,
    predictions,
    training_case_ids=None,
    data_gate_passed=False,
):
    """Calculate metrics only after explicit approval of the T004 data gate."""
    failures = []

    if data_gate_passed is not True:
        failures.append({
            "stage": "classification_quality",
            "code": "DATA_GATE_NOT_PASSED",
            "message": "Quality evaluation blocked because the T004 data gate has not passed.",
        })
        dataset_valid = False
        cases = []
    else:
        try:
            cases = load_evaluation_manifest(manifest_path)
            dataset_valid = validate_evaluation_manifest(
                cases,
                training_case_ids=training_case_ids,
            )
        except (ValueError, OSError, json.JSONDecodeError):
            cases = []
            dataset_valid = False

        if not dataset_valid:
            failures.append({
                "stage": "classification_quality",
                "code": "EVALUATION_DATASET_INVALID",
                "message": "Evaluation manifest failed validation.",
            })

    if dataset_valid:
        try:
            quality_cases = select_quality_cases(cases)
            metrics = calculate_classification_metrics(
                quality_cases,
                predictions,
            )
        except (ValueError, KeyError, TypeError) as exc:
            failures.append({
                "stage": "classification_quality",
                "code": "METRIC_CALCULATION_FAILED",
                "message": str(exc),
            })
            metrics = calculate_classification_metrics([], {})
    else:
        metrics = calculate_classification_metrics([], {})

    passed = (
        dataset_valid
        and not failures
        and metrics["macro_f1"] >= QUALITY_THRESHOLD
    )

    if dataset_valid and metrics["macro_f1"] < QUALITY_THRESHOLD:
        failures.append({
            "stage": "classification_quality",
            "code": "MACRO_F1_BELOW_THRESHOLD",
            "message": "Macro-F1 is below the required 0.80 threshold.",
        })

    return {
        "passed": passed,
        "evaluation_dataset_valid": dataset_valid,
        "metrics": metrics,
        "failure_evidence": failures,
    }