import pytest

from spam_classifier.classifier import apply_review_threshold


@pytest.mark.parametrize(
    ("confidence", "expected"),
    [
        (0.699, "REVIEW"),
        (0.700, "HAM"),
        (0.701, "HAM"),
    ],
)
def test_review_threshold_boundary(confidence, expected):
    result = apply_review_threshold("HAM", confidence)
    assert result == expected


@pytest.mark.parametrize("predicted_class", ["SPAM", "HAM"])
@pytest.mark.parametrize("confidence", [0.700, 0.701])
def test_confidence_at_or_above_threshold_returns_predicted_class(
    predicted_class, confidence
):
    result = apply_review_threshold(predicted_class, confidence)
    assert result == predicted_class


@pytest.mark.parametrize("confidence", [-0.01, 1.01, float("nan"), float("inf")])
def test_invalid_confidence_is_rejected(confidence):
    with pytest.raises(ValueError):
        apply_review_threshold("HAM", confidence)


@pytest.mark.parametrize("predicted_class", ["REVIEW", "UNKNOWN", "", None, 123])
def test_invalid_predicted_class_is_rejected(predicted_class):
    with pytest.raises(ValueError):
        apply_review_threshold(predicted_class, 0.85)
