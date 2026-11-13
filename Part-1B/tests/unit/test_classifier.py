import math

import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from spam_classifier.classifier import (
    apply_review_threshold,
    classify_message,
)


@pytest.fixture(scope="module")
def fitted_model():
    """Fit a small deterministic model using synthetic examples only."""
    messages = [
        "Win a free prize now",
        "Congratulations claim your cash reward",
        "Limited offer click to win",
        "You have won a free gift",
        "Are we meeting for lunch today",
        "Please call me when you arrive",
        "Can you send the project report",
        "Thank you for your help",
    ]
    labels = [
        "SPAM",
        "SPAM",
        "SPAM",
        "SPAM",
        "HAM",
        "HAM",
        "HAM",
        "HAM",
    ]

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", MultinomialNB()),
        ]
    )
    model.fit(messages, labels)
    return model


@pytest.mark.unit
def test_classifies_valid_english_message(fitted_model):
    result = classify_message(
        fitted_model,
        "Please send me the project report today.",
    )

    assert isinstance(result, dict)
    assert result["category"] in {"SPAM", "HAM", "REVIEW"}


@pytest.mark.unit
def test_result_category_is_allowed(fitted_model):
    result = classify_message(
        fitted_model,
        "Congratulations, you have won a free prize.",
    )

    assert result["category"] in {"SPAM", "HAM", "REVIEW"}


@pytest.mark.unit
def test_confidence_is_finite_and_between_zero_and_one(fitted_model):
    result = classify_message(
        fitted_model,
        "Can you please call me tomorrow?",
    )

    confidence = result["confidence"]

    assert isinstance(confidence, (int, float))
    assert math.isfinite(confidence)
    assert 0 <= confidence <= 1


@pytest.mark.unit
def test_same_model_and_message_produce_repeatable_result(fitted_model):
    message = "Congratulations, claim your free reward now."

    first_result = classify_message(fitted_model, message)
    second_result = classify_message(fitted_model, message)

    assert first_result == second_result


@pytest.mark.unit
def test_confidence_is_maximum_class_probability(fitted_model):
    message = "You have won a free prize."

    result = classify_message(fitted_model, message)

    probabilities = fitted_model.predict_proba([message])[0]
    maximum_index = max(
        range(len(probabilities)),
        key=lambda index: probabilities[index],
    )

    expected_confidence = float(probabilities[maximum_index])
    predicted_class = str(fitted_model.classes_[maximum_index])
    expected_category = apply_review_threshold(
        predicted_class,
        expected_confidence,
    )

    assert result["confidence"] == pytest.approx(expected_confidence)
    assert result["category"] == expected_category
