import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "specs"
    / "001-customer-message-spam-classifier"
    / "contracts"
    / "classification-result.schema.json"
)


@pytest.fixture(scope="module")
def result_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    Draft202012Validator.check_schema(schema)
    return schema


@pytest.fixture(scope="module")
def validator(result_schema):
    return Draft202012Validator(result_schema)


@pytest.mark.contract
@pytest.mark.parametrize(
    "result",
    [
        {"category": "SPAM", "confidence": 0.95},
        {"category": "HAM", "confidence": 0.85},
        {"category": "REVIEW", "confidence": 0.65},
    ],
)
def test_valid_classification_results(validator, result):
    validator.validate(result)


@pytest.mark.contract
@pytest.mark.parametrize(
    "result",
    [
        {"category": "UNKNOWN", "confidence": 0.85},
        {"category": "HAM", "confidence": -0.01},
        {"category": "SPAM", "confidence": 1.01},
        {"category": "HAM"},
        {"confidence": 0.85},
        {"category": "HAM", "confidence": 0.85, "extra": "unexpected"},
    ],
)
def test_invalid_classification_results_are_rejected(validator, result):
    assert not validator.is_valid(result)


@pytest.mark.contract
def test_result_contains_exactly_category_and_confidence(validator):
    result = {"category": "HAM", "confidence": 0.85}

    validator.validate(result)

    assert set(result.keys()) == {"category", "confidence"}
