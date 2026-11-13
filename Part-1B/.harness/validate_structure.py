"""JSON Schema validation for classification results and evaluation reports."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "specs" / "001-customer-message-spam-classifier" / "contracts"

SCHEMAS = {
    "result": CONTRACTS / "classification-result.schema.json",
    "error": CONTRACTS / "classification-error.schema.json",
    "report": CONTRACTS / "evaluation-report.schema.json",
}


def _load_schema(path):
    with path.open("r", encoding="utf-8-sig") as file:
        schema = json.load(file)
    Draft202012Validator.check_schema(schema)
    return schema


def validate_structure(result_payloads=None, report_payload=None):
    """Validate result/error payloads and the evaluation report independently."""
    failures = []

    try:
        schemas = {name: _load_schema(path) for name, path in SCHEMAS.items()}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "passed": False,
            "failure_evidence": [{
                "stage": "structural_validation",
                "code": "SCHEMA_LOAD_FAILED",
                "message": str(exc),
            }],
        }

    if result_payloads is None:
        result_payloads = []
    elif isinstance(result_payloads, dict):
        result_payloads = [result_payloads]

    if not isinstance(result_payloads, list):
        failures.append({
            "stage": "structural_validation",
            "code": "RESULT_PAYLOADS_INVALID",
            "message": "Classification results must be supplied as a list or object.",
        })
    else:
        for index, payload in enumerate(result_payloads):
            schema_name = "error" if isinstance(payload, dict) and "error" in payload else "result"
            validator = Draft202012Validator(schemas[schema_name])

            errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
            for error in errors:
                failures.append({
                    "stage": "structural_validation",
                    "code": "RESULT_SCHEMA_INVALID",
                    "message": f"Result {index}: {error.message}",
                })

    if report_payload is None:
        failures.append({
            "stage": "structural_validation",
            "code": "REPORT_MISSING",
            "message": "Evaluation report payload is required.",
        })
    else:
        validator = Draft202012Validator(schemas["report"])
        for error in sorted(
            validator.iter_errors(report_payload),
            key=lambda item: list(item.path),
        ):
            failures.append({
                "stage": "structural_validation",
                "code": "REPORT_SCHEMA_INVALID",
                "message": error.message,
            })

    return {"passed": not failures, "failure_evidence": failures}
