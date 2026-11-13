"""Run the complete spam-classifier evaluation harness."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / ".harness"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HARNESS_DIR))

from spam_classifier.classifier import classify_message
from spam_classifier.evaluation import load_evaluation_manifest
from spam_classifier.classifier import train_model
from spam_classifier.validation import validate_message

from evaluate_quality import evaluate_quality
from validate_data_gate import validate_data_gate
from validate_invariants import validate_invariants
from validate_structure import validate_structure


QUALITY_THRESHOLD = 0.80


def _run_stage(stage):
    """Execute a stage callable or return an already-computed result."""
    return stage() if callable(stage) else stage


def _failure_evidence(stage_result):
    evidence = stage_result.get("failure_evidence", [])
    return evidence if isinstance(evidence, list) else []


def _build_report(
    structural_pass,
    invariant_pass,
    quality,
    failure_evidence,
):
    metrics = quality.get("metrics", {})

    dataset_valid = quality.get("evaluation_dataset_valid") is True
    macro_f1 = metrics.get("macro_f1", 0.0)

    quality_pass = (
        quality.get("passed") is True
        and dataset_valid
        and isinstance(macro_f1, (int, float))
        and macro_f1 >= QUALITY_THRESHOLD
    )

    overall_pass = (
        structural_pass
        and invariant_pass
        and dataset_valid
        and quality_pass
    )

    return {
        "structural_validation_pass": structural_pass,
        "invariant_validation_pass": invariant_pass,
        "evaluation_dataset_valid": dataset_valid,
        "classification_quality_pass": quality_pass,
        "overall_pass": overall_pass,
        "failure_evidence": failure_evidence,
        "spam_precision": metrics.get("spam_precision", 0.0),
        "spam_recall": metrics.get("spam_recall", 0.0),
        "spam_f1": metrics.get("spam_f1", 0.0),
        "ham_precision": metrics.get("ham_precision", 0.0),
        "ham_recall": metrics.get("ham_recall", 0.0),
        "ham_f1": metrics.get("ham_f1", 0.0),
        "macro_f1": macro_f1,
        "review_count": metrics.get("review_count", 0),
        "review_rate": metrics.get("review_rate", 0.0),
        "total_valid_evaluation_case_count": metrics.get(
            "total_valid_evaluation_case_count", 0
        ),
        "human_decision": None,
    }


def run_pipeline(
    structural_stage,
    invariant_stage,
    quality_stage,
    output_path="eval-results.json",
):
    """Run all evaluation stages and save the combined report."""
    structural = _run_stage(structural_stage)
    invariant = _run_stage(invariant_stage)
    quality = _run_stage(quality_stage)

    structural_pass = structural.get("passed") is True
    invariant_pass = invariant.get("passed") is True

    failures = (
        _failure_evidence(structural)
        + _failure_evidence(invariant)
        + _failure_evidence(quality)
    )

    report = _build_report(
        structural_pass,
        invariant_pass,
        quality,
        failures,
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    return report


def _validation_error_payload(message):
    """Convert an input validation exception to the public error contract."""
    error_codes = {
        "Message is required.": "MESSAGE_REQUIRED",
        "Message must be text.": "MESSAGE_INVALID_TYPE",
        "Message cannot be empty.": "MESSAGE_EMPTY",
    }

    return {
        "error": error_codes.get(str(message), "VALIDATION_ERROR"),
        "message": str(message),
    }


def _evaluate_cases(model, cases):
    """Evaluate valid messages and exercise validation-only cases."""
    result_payloads = []
    predictions = {}
    runner_failures = []

    for case in cases:
        case_id = case["case_id"]
        group = case["case_group"]
        message = case.get("message")

        if group == "validation_only":
            try:
                validate_message(message)
                runner_failures.append({
                    "stage": "runner",
                    "code": "EXPECTED_VALIDATION_ERROR",
                    "message": (
                        f"Validation-only case {case_id} was accepted."
                    ),
                })
                result_payloads.append({
                    "error": "EXPECTED_VALIDATION_ERROR",
                    "message": "The input was expected to fail validation.",
                })
            except ValueError as exc:
                payload = _validation_error_payload(exc)
                result_payloads.append(payload)

                if payload["error"] != case.get("expected_error"):
                    runner_failures.append({
                        "stage": "runner",
                        "code": "VALIDATION_ERROR_MISMATCH",
                        "message": (
                            f"Validation-only case {case_id} produced "
                            "an unexpected error code."
                        ),
                    })
            except Exception:
                result_payloads.append({
                    "error": "VALIDATION_FAILED",
                    "message": "Input validation could not be completed.",
                })
                runner_failures.append({
                    "stage": "runner",
                    "code": "VALIDATION_FAILED",
                    "message": (
                        f"Validation-only case {case_id} raised "
                        "an unexpected exception."
                    ),
                })

            continue

        try:
            result = classify_message(model, message)
            result_payloads.append(result)

            if group == "synthetic_held_out":
                predictions[case_id] = result["category"]

        except Exception:
            result_payloads.append({
                "error": "CLASSIFICATION_FAILED",
                "message": "The message could not be classified.",
            })
            runner_failures.append({
                "stage": "runner",
                "code": "CLASSIFICATION_FAILED",
                "message": (
                    f"Evaluation case {case_id} could not be classified."
                ),
            })

    return result_payloads, predictions, runner_failures


def main():
    """Execute the real data, model, structural, invariant and quality stages."""
    manifest_path = ROOT / "evals" / "dataset.json"
    output_path = ROOT / "eval-results.json"

    data_gate = validate_data_gate()
    cases = load_evaluation_manifest(manifest_path)

    runner_failures = []

    if data_gate.get("passed") is True:
        model = train_model(ROOT / "data" / "training.json")
        result_payloads, predictions, case_failures = _evaluate_cases(
            model,
            cases,
        )
        runner_failures.extend(case_failures)
    else:
        result_payloads = []
        predictions = []

        runner_failures.extend(data_gate.get("failure_evidence", []))

    quality = evaluate_quality(
        manifest_path=manifest_path,
        predictions=predictions,
        data_gate_passed=data_gate.get("passed") is True,
    )

    runner_failures.extend(quality.get("failure_evidence", []))

    provisional = _build_report(
        True,
        True,
        quality,
        runner_failures,
    )

    structural = validate_structure(
        result_payloads=result_payloads,
        report_payload=provisional,
    )

    provisional = _build_report(
        structural.get("passed") is True,
        True,
        quality,
        runner_failures
        + structural.get("failure_evidence", []),
    )

    invariant = validate_invariants(
        report=provisional,
        manifest_path=manifest_path,
    )

    report = run_pipeline(
        structural_stage=structural,
        invariant_stage=invariant,
        quality_stage=quality,
        output_path=output_path,
    )

    print(json.dumps(report, indent=2))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
