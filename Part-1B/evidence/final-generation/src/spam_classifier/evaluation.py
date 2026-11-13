"""Evaluation manifest validation, classification metrics, and report invariants."""

import json
import math
from pathlib import Path

VALID_GROUPS = {
    "synthetic_held_out",
    "synthetic_controlled",
    "validation_only",
}

VALID_SCENARIOS = {
    "normal",
    "boundary",
    "ambiguous",
    "adversarial",
    "missing",
    "malformed",
}

QUALITY_SCENARIOS = {
    "normal",
    "boundary",
    "ambiguous",
    "adversarial",
}

VALID_LABELS = {"SPAM", "HAM"}
VALID_PREDICTIONS = {"SPAM", "HAM", "REVIEW"}

VALID_REQUIREMENT_REFS = {
    *(f"FR-{number:03d}" for number in range(1, 16)),
    *(f"SC-{number:03d}" for number in range(1, 9)),
}

QUALITY_THRESHOLD = 0.80
MIN_HELD_OUT_CASES = 15
MIN_CASES_PER_CLASS = 5


def load_evaluation_manifest(path):
    """Load a JSON evaluation manifest without modifying its cases."""
    try:
        with Path(path).open("r", encoding="utf-8") as file:
            manifest = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Unable to load evaluation manifest.") from exc

    if isinstance(manifest, dict):
        cases = manifest.get("cases")
    else:
        cases = manifest

    if not isinstance(cases, list):
        raise ValueError("Evaluation manifest must contain a list of cases.")

    return cases


def validate_evaluation_manifest(cases, training_case_ids=None):
    """Validate synthetic evaluation cases and their required coverage."""
    if not isinstance(cases, list):
        return False

    if training_case_ids is not None:
        if not isinstance(training_case_ids, (list, tuple, set)):
            return False
        try:
            training_ids = set(training_case_ids)
        except TypeError:
            return False
    else:
        training_ids = set()

    case_ids = set()
    held_out_cases = []
    held_out_scenarios = set()
    controlled_scenarios = set()
    missing_cases = 0
    malformed_cases = 0

    try:
        for case in cases:
            if not isinstance(case, dict):
                return False

            case_id = case.get("case_id")
            group = case.get("case_group")
            scenario = case.get("scenario")
            refs = case.get("requirement_refs")

            if not isinstance(case_id, str) or not case_id.strip():
                return False

            if case_id in case_ids or case_id in training_ids:
                return False

            case_ids.add(case_id)

            if group not in VALID_GROUPS or scenario not in VALID_SCENARIOS:
                return False

            if (
                not isinstance(refs, list)
                or not refs
                or any(
                    not isinstance(ref, str)
                    or ref not in VALID_REQUIREMENT_REFS
                    for ref in refs
                )
            ):
                return False

            if group in {"synthetic_held_out", "synthetic_controlled"}:
                message = case.get("message")
                label = case.get("expected_label")
                error = case.get("expected_error")

                if (
                    not isinstance(message, str)
                    or not message.strip()
                    or label not in VALID_LABELS
                    or error is not None
                    or scenario not in QUALITY_SCENARIOS
                ):
                    return False

                if group == "synthetic_held_out":
                    held_out_cases.append(case)
                    held_out_scenarios.add(scenario)
                else:
                    controlled_scenarios.add(scenario)

            elif group == "validation_only":
                label = case.get("expected_label")
                error = case.get("expected_error")

                if label is not None:
                    return False

                if not isinstance(error, str) or not error.strip():
                    return False

                if scenario == "missing":
                    if case.get("message") is not None:
                        return False
                    missing_cases += 1

                elif scenario == "malformed":
                    message = case.get("message")
                    if isinstance(message, str):
                        return False
                    if "message" not in case:
                        return False
                    malformed_cases += 1

                else:
                    return False

        spam_count = sum(
            case["expected_label"] == "SPAM" for case in held_out_cases
        )
        ham_count = sum(
            case["expected_label"] == "HAM" for case in held_out_cases
        )

        all_quality_scenarios = held_out_scenarios | controlled_scenarios

        return (
            len(held_out_cases) >= MIN_HELD_OUT_CASES
            and spam_count >= MIN_CASES_PER_CLASS
            and ham_count >= MIN_CASES_PER_CLASS
            and all_quality_scenarios == QUALITY_SCENARIOS
            and missing_cases >= 1
            and malformed_cases >= 1
        )

    except (KeyError, TypeError, ValueError):
        return False


def calculate_classification_metrics(cases, predictions):
    """Calculate SPAM/HAM metrics using only synthetic held-out cases."""
    if not isinstance(cases, list) or not isinstance(predictions, dict):
        raise ValueError("Invalid evaluation cases or predictions.")

    quality_cases = select_quality_cases(cases)
    expected_case_ids = {
        case["case_id"] for case in quality_cases
    }

    if set(predictions) != expected_case_ids:
        raise ValueError(
            "Prediction IDs must exactly match synthetic held-out evaluation cases."
        )

    spam_tp = 0
    spam_fp = 0
    spam_fn = 0

    ham_tp = 0
    ham_fp = 0
    ham_fn = 0

    review_count = 0

    for case in quality_cases:
        case_id = case["case_id"]
        true_label = case["expected_label"]
        predicted_label = predictions[case_id]

        if true_label not in VALID_LABELS:
            raise ValueError("Invalid ground-truth evaluation label.")

        if predicted_label not in VALID_PREDICTIONS:
            raise ValueError("Invalid classification prediction.")

        if predicted_label == "REVIEW":
            review_count += 1

            if true_label == "SPAM":
                spam_fn += 1
            else:
                ham_fn += 1

        elif true_label == "SPAM":
            if predicted_label == "SPAM":
                spam_tp += 1
            else:
                spam_fn += 1
                ham_fp += 1

        else:
            if predicted_label == "HAM":
                ham_tp += 1
            else:
                ham_fn += 1
                spam_fp += 1

    spam_predicted = spam_tp + spam_fp
    ham_predicted = ham_tp + ham_fp

    spam_actual = spam_tp + spam_fn
    ham_actual = ham_tp + ham_fn

    spam_precision = (
        spam_tp / spam_predicted if spam_predicted else 0
    )
    spam_recall = spam_tp / spam_actual if spam_actual else 0

    ham_precision = (
        ham_tp / ham_predicted if ham_predicted else 0
    )
    ham_recall = ham_tp / ham_actual if ham_actual else 0

    spam_f1 = (
        2 * spam_precision * spam_recall
        / (spam_precision + spam_recall)
        if spam_precision + spam_recall
        else 0
    )

    ham_f1 = (
        2 * ham_precision * ham_recall
        / (ham_precision + ham_recall)
        if ham_precision + ham_recall
        else 0
    )

    macro_f1 = (spam_f1 + ham_f1) / 2
    total_cases = len(quality_cases)

    review_rate = (
        review_count / total_cases if total_cases > 0 else 0
    )

    return {
        "spam_precision": spam_precision,
        "spam_recall": spam_recall,
        "spam_f1": spam_f1,
        "ham_precision": ham_precision,
        "ham_recall": ham_recall,
        "ham_f1": ham_f1,
        "macro_f1": macro_f1,
        "review_count": review_count,
        "review_rate": review_rate,
        "total_valid_evaluation_case_count": total_cases,
    }


def validate_report_invariants(report):
    """Check report-level invariants independently of JSON Schema."""
    if not isinstance(report, dict):
        return False

    required_fields = {
        "structural_validation_pass",
        "invariant_validation_pass",
        "evaluation_dataset_valid",
        "classification_quality_pass",
        "overall_pass",
        "failure_evidence",
        "spam_precision",
        "spam_recall",
        "spam_f1",
        "ham_precision",
        "ham_recall",
        "ham_f1",
        "macro_f1",
        "review_count",
        "review_rate",
        "total_valid_evaluation_case_count",
        "human_decision",
    }

    if not required_fields.issubset(report):
        return False

    boolean_fields = {
        "structural_validation_pass",
        "invariant_validation_pass",
        "evaluation_dataset_valid",
        "classification_quality_pass",
        "overall_pass",
    }

    if any(type(report[field]) is not bool for field in boolean_fields):
        return False

    if report["human_decision"] is not None:
        return False

    if not isinstance(report["failure_evidence"], list):
        return False

    numeric_fields = {
        "spam_precision",
        "spam_recall",
        "spam_f1",
        "ham_precision",
        "ham_recall",
        "ham_f1",
        "macro_f1",
        "review_rate",
    }

    for field in numeric_fields:
        value = report[field]

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            return False

    review_count = report["review_count"]
    total_cases = report["total_valid_evaluation_case_count"]

    if (
        type(review_count) is not int
        or type(total_cases) is not int
        or review_count < 0
        or total_cases < 0
        or review_count > total_cases
    ):
        return False

    expected_review_rate = (
        review_count / total_cases if total_cases > 0 else 0
    )

    if not math.isclose(
        report["review_rate"],
        expected_review_rate,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        return False

    expected_macro_f1 = (
        report["spam_f1"] + report["ham_f1"]
    ) / 2

    if not math.isclose(
        report["macro_f1"],
        expected_macro_f1,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        return False

    expected_quality_pass = (
        report["evaluation_dataset_valid"]
        and report["macro_f1"] >= QUALITY_THRESHOLD
    )

    if report["classification_quality_pass"] != expected_quality_pass:
        return False

    expected_overall_pass = (
        report["structural_validation_pass"]
        and report["invariant_validation_pass"]
        and report["evaluation_dataset_valid"]
        and report["classification_quality_pass"]
    )

    return report["overall_pass"] == expected_overall_pass


def select_quality_cases(cases):
    """Select synthetic held-out cases for classification-quality metrics."""
    if not isinstance(cases, list):
        raise ValueError("Evaluation cases must be a list.")

    return [
        case
        for case in cases
        if isinstance(case, dict)
        and case.get("case_group") == "synthetic_held_out"
        and case.get("expected_label") in VALID_LABELS
        and isinstance(case.get("message"), str)
        and bool(case["message"].strip())
        and case.get("expected_error") is None
    ]