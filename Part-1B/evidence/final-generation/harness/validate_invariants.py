
"""Invariant and dataset validation stage."""

import json

from spam_classifier.evaluation import (
    load_evaluation_manifest,
    validate_evaluation_manifest,
    validate_report_invariants,
)


def validate_invariants(report, manifest_path, training_case_ids=None):
    """Validate manifest separation and report-level invariants."""
    failures = []

    try:
        cases = load_evaluation_manifest(manifest_path)
        dataset_valid = validate_evaluation_manifest(
            cases,
            training_case_ids=training_case_ids,
        )
    except (ValueError, OSError, json.JSONDecodeError):
        dataset_valid = False
        failures.append({
            "stage": "invariant_validation",
            "code": "MANIFEST_LOAD_FAILED",
            "message": "Unable to load or validate the evaluation manifest.",
        })

    if not dataset_valid:
        failures.append({
            "stage": "invariant_validation",
            "code": "EVALUATION_DATASET_INVALID",
            "message": (
                "Evaluation manifest failed validation "
                "or training-data separation."
            ),
        })

    if not isinstance(report, dict):
        failures.append({
            "stage": "invariant_validation",
            "code": "REPORT_INVALID",
            "message": "Evaluation report must be an object.",
        })
    else:
        reported_dataset_valid = report.get("evaluation_dataset_valid")

        if reported_dataset_valid is not dataset_valid:
            failures.append({
                "stage": "invariant_validation",
                "code": "DATASET_VALIDITY_MISMATCH",
                "message": (
                    "Reported dataset validity does not match "
                    "manifest validation."
                ),
            })

        if not validate_report_invariants(report):
            failures.append({
                "stage": "invariant_validation",
                "code": "REPORT_INVARIANT_FAILED",
                "message": "One or more evaluation report invariants failed.",
            })

        if report.get("human_decision") is not None:
            failures.append({
                "stage": "invariant_validation",
                "code": "HUMAN_DECISION_NOT_NULL",
                "message": "Automated evaluation must leave human_decision null.",
            })

    return {
        "passed": not failures,
        "evaluation_dataset_valid": dataset_valid,
        "failure_evidence": failures,
    }
