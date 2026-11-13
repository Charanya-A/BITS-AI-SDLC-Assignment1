"""Verify the reviewed synthetic datasets before model training."""

import hashlib
import json
from pathlib import Path

from spam_classifier.evaluation import validate_evaluation_manifest

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_HASHES = {
    "data/training.json": (
        "F5865B32B537F28FE5EB0B9AFD7C9DCD82A6A2A6E4AB58EDB530DA83E5B6D269"
    ),
    "evals/dataset.json": (
        "7957212B7D931E55CE267F89EADB64D8C90138AD5FC491511B1161304174414D"
    ),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_data_gate():
    failures = []

    for relative_path, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative_path
        if not path.is_file():
            failures.append({
                "code": "DATA_FILE_MISSING",
                "message": f"Required data file is missing: {relative_path}",
            })
            continue

        if sha256(path) != expected_hash:
            failures.append({
                "code": "DATA_HASH_MISMATCH",
                "message": f"Reviewed data file has changed: {relative_path}",
            })

    training_path = ROOT / "data" / "training.json"
    manifest_path = ROOT / "evals" / "dataset.json"
    readme_path = ROOT / "data" / "README.md"

    training = []
    cases = []

    try:
        training = json.loads(training_path.read_text(encoding="utf-8"))["examples"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        failures.append({
            "code": "TRAINING_DATA_INVALID",
            "message": "Training dataset could not be loaded.",
        })

    try:
        cases = json.loads(manifest_path.read_text(encoding="utf-8"))["cases"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        failures.append({
            "code": "EVALUATION_DATA_INVALID",
            "message": "Evaluation manifest could not be loaded.",
        })

    if training:
        labels = [item.get("label") for item in training]
        if (
            len(training) != 40
            or labels.count("SPAM") != 20
            or labels.count("HAM") != 20
            or any(
                not isinstance(item.get("message"), str)
                or not item["message"].strip()
                for item in training
            )
        ):
            failures.append({
                "code": "TRAINING_COUNTS_INVALID",
                "message": "Training dataset must contain 40 valid examples: 20 SPAM and 20 HAM.",
            })

    if cases:
        if not validate_evaluation_manifest(cases):
            failures.append({
                "code": "EVALUATION_MANIFEST_INVALID",
                "message": "Evaluation manifest failed project validation.",
            })

        groups = [case.get("case_group") for case in cases]
        heldout = [
            case for case in cases
            if case.get("case_group") == "synthetic_held_out"
        ]
        controlled = [
            case for case in cases
            if case.get("case_group") == "synthetic_controlled"
        ]
        validation = [
            case for case in cases
            if case.get("case_group") == "validation_only"
        ]

        if (
            len(cases) != 22
            or len(heldout) != 16
            or len(controlled) != 4
            or len(validation) != 2
            or sum(case.get("expected_label") == "SPAM" for case in heldout) != 8
            or sum(case.get("expected_label") == "HAM" for case in heldout) != 8
        ):
            failures.append({
                "code": "EVALUATION_COUNTS_INVALID",
                "message": "Evaluation dataset group counts or held-out label balance are incorrect.",
            })

    if training and cases:
        training_messages = {
            item["message"].strip().casefold()
            for item in training
            if isinstance(item.get("message"), str)
        }
        evaluation_messages = {
            case["message"].strip().casefold()
            for case in cases
            if isinstance(case.get("message"), str) and case["message"].strip()
        }

        if training_messages & evaluation_messages:
            failures.append({
                "code": "DATA_SEPARATION_FAILED",
                "message": "An exact message appears in both training and evaluation data.",
            })

    try:
        documentation = readme_path.read_text(encoding="utf-8")
        required_phrases = [
            "manually reviewed and approved",
            "Review outcome: Approved.",
            "Review date: 2026-11-13.",
            "No UCI SMS Spam Collection messages",
            "Only `synthetic_held_out` cases contribute",
        ]
        if any(phrase not in documentation for phrase in required_phrases):
            failures.append({
                "code": "DATA_DOCUMENTATION_INCOMPLETE",
                "message": "Dataset documentation is missing required provenance or approval statements.",
            })
    except OSError:
        failures.append({
            "code": "DATA_DOCUMENTATION_MISSING",
            "message": "Dataset documentation could not be read.",
        })

    return {
        "passed": not failures,
        "failure_evidence": failures,
    }


if __name__ == "__main__":
    print(json.dumps(validate_data_gate(), indent=2))
