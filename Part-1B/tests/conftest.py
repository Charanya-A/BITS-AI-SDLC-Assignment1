import pytest


@pytest.fixture
def valid_message():
    """Provide a simple valid English customer message."""
    return "Hello, I would like to know more about your service."


@pytest.fixture
def confidence_result():
    """Provide a deterministic classification confidence result."""
    return {
        "predicted_label": "HAM",
        "confidence": 0.85,
        "decision": "HAM",
    }


@pytest.fixture
def review_confidence_result():
    """Provide a result below the REVIEW threshold."""
    return {
        "predicted_label": "HAM",
        "confidence": 0.699,
        "decision": "REVIEW",
    }
