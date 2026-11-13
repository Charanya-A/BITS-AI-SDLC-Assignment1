"""TF-IDF and Multinomial Naive Bayes training and classification."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from spam_classifier.data import load_training_data
from spam_classifier.validation import validate_message

REVIEW_THRESHOLD = 0.70


def train_model(training_path):
    """Fit TF-IDF and Multinomial Naive Bayes using training data only."""
    messages, labels = load_training_data(training_path)

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                sublinear_tf=True,
            ),
        ),
        ("classifier", MultinomialNB(alpha=0.01)),
    ])

    pipeline.fit(messages, labels)
    return pipeline


def apply_review_threshold(predicted_class: str, confidence: float) -> str:
    """Return REVIEW below 0.70; otherwise return the predicted class."""
    if not isinstance(predicted_class, str) or predicted_class not in {"SPAM", "HAM"}:
        raise ValueError("predicted_class must be SPAM or HAM")

    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise ValueError("confidence must be a number between 0 and 1")

    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    return "REVIEW" if confidence < REVIEW_THRESHOLD else predicted_class


def classify_message(model, message: str) -> dict:
    """Classify one valid message using an already-fitted model.

    Confidence is the maximum predicted class probability estimate.
    It is not guaranteed to be a calibrated probability of correctness.
    """
    valid_message = validate_message(message)

    predicted_probabilities = model.predict_proba([valid_message])[0]
    maximum_index = max(
        range(len(predicted_probabilities)),
        key=lambda index: predicted_probabilities[index],
    )

    confidence = float(predicted_probabilities[maximum_index])
    predicted_class = str(model.classes_[maximum_index])
    category = apply_review_threshold(predicted_class, confidence)

    return {
        "category": category,
        "confidence": confidence,
    }
