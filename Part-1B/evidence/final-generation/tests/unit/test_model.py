import json

import pytest

from spam_classifier.data import load_training_data
from spam_classifier.classifier import train_model


def test_load_training_data_returns_messages_and_labels(tmp_path):
    path = tmp_path / "training.json"
    path.write_text(
        json.dumps({
            "examples": [
                {"message": "Claim your reward now.", "label": "SPAM"},
                {"message": "Meeting starts tomorrow.", "label": "HAM"},
            ]
        }),
        encoding="utf-8",
    )

    messages, labels = load_training_data(path)

    assert len(messages) == 2
    assert labels == ["SPAM", "HAM"]


def test_load_training_data_rejects_invalid_label(tmp_path):
    path = tmp_path / "training.json"
    path.write_text(
        json.dumps({
            "examples": [
                {"message": "Hello there.", "label": "OTHER"},
                {"message": "Meeting tomorrow.", "label": "HAM"},
            ]
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="SPAM or HAM"):
        load_training_data(path)


def test_load_training_data_rejects_empty_message(tmp_path):
    path = tmp_path / "training.json"
    path.write_text(
        json.dumps({
            "examples": [
                {"message": " ", "label": "SPAM"},
                {"message": "Meeting tomorrow.", "label": "HAM"},
            ]
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty"):
        load_training_data(path)


def test_train_model_fits_tfidf_and_naive_bayes(tmp_path):
    path = tmp_path / "training.json"
    path.write_text(
        json.dumps({
            "examples": [
                {"message": "Claim your cash prize now.", "label": "SPAM"},
                {"message": "Win a special reward today.", "label": "SPAM"},
                {"message": "Meeting starts tomorrow morning.", "label": "HAM"},
                {"message": "Please review the project report.", "label": "HAM"},
            ]
        }),
        encoding="utf-8",
    )

    model = train_model(path)

    assert model.named_steps["tfidf"].vocabulary_
    assert model.named_steps["classifier"].classes_.tolist() == ["HAM", "SPAM"]
    assert len(model.predict(["Claim your prize now."])) == 1


def test_load_training_data_rejects_missing_file(tmp_path):
    with pytest.raises(ValueError, match="could not be loaded"):
        load_training_data(tmp_path / "missing.json")

