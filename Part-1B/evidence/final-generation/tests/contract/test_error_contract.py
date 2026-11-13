import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "specs"
    / "001-customer-message-spam-classifier"
    / "contracts"
    / "classification-error.schema.json"
)


@pytest.fixture(scope="module")
def error_validator():
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.mark.contract
def test_safe_error_response_matches_schema(error_validator):
    response = {
        "error": "Invalid input",
        "message": "Please enter a valid customer message.",
    }

    error_validator.validate(response)


@pytest.mark.contract
@pytest.mark.parametrize(
    "response",
    [
        {"error": "", "message": "Please try again."},
        {"error": "Invalid input", "message": ""},
        {"error": "Invalid input"},
        {"message": "Please try again."},
        {
            "error": "Invalid input",
            "message": "Please try again.",
            "debug": "internal details",
        },
    ],
)
def test_invalid_error_responses_are_rejected(error_validator, response):
    assert not error_validator.is_valid(response)


def contains_stack_trace(text):
    patterns = [
        r"Traceback \(most recent call last\)",
        r'File ".*", line \d+',
        r"\b[A-Za-z]+Error:",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def contains_local_path(text):
    windows_path = re.search(r"[A-Za-z]:\\", text)
    unix_path = re.search(r"(?:^|\s)/(?:[^/\s]+/)+[^/\s]*", text)
    return windows_path is not None or unix_path is not None


def assert_safe_error_response(response, submitted_message):
    combined_text = " ".join(response.values())

    assert all(isinstance(value, str) and value.strip() for value in response.values())
    assert submitted_message.casefold() not in combined_text.casefold()
    assert not contains_stack_trace(combined_text)
    assert not contains_local_path(combined_text)


@pytest.mark.contract
def test_error_response_does_not_echo_submitted_message(error_validator):
    submitted_message = "My private account number is 123456789."

    response = {
        "error": "Invalid input",
        "message": "Please enter a valid customer message.",
    }

    error_validator.validate(response)
    assert_safe_error_response(response, submitted_message)


@pytest.mark.contract
@pytest.mark.parametrize(
    "unsafe_text",
    [
        'Traceback (most recent call last)',
        'File "C:\\Users\\student\\project\\app.py", line 42',
        "ValueError: invalid input",
        "Error occurred at /home/student/project/app.py",
    ],
)
def test_error_response_does_not_expose_stack_traces_or_local_paths(
    error_validator, unsafe_text
):
    response = {
        "error": "Processing failed",
        "message": unsafe_text,
    }

    error_validator.validate(response)

    with pytest.raises(AssertionError):
        assert_safe_error_response(response, "Original submitted message")
