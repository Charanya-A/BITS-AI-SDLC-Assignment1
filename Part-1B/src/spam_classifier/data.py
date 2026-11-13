"""Load and validate self-authored synthetic training data."""

import json
from pathlib import Path


def load_training_data(path):
    """Load and validate the self-authored synthetic training examples."""
    dataset_path = Path(path)

    try:
        payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Training dataset could not be loaded.") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("examples"), list):
        raise ValueError("Training dataset must contain an examples list.")

    examples = payload["examples"]
    if len(examples) < 2:
        raise ValueError("Training dataset must contain at least two examples.")

    messages = []
    labels = []

    for example in examples:
        if not isinstance(example, dict):
            raise ValueError("Each training example must be an object.")

        message = example.get("message")
        label = example.get("label")

        if not isinstance(message, str) or not message.strip():
            raise ValueError("Training messages must be non-empty text.")

        if label not in {"SPAM", "HAM"}:
            raise ValueError("Training labels must be SPAM or HAM.")

        messages.append(message.strip())
        labels.append(label)

    if set(labels) != {"SPAM", "HAM"}:
        raise ValueError("Training data must contain both SPAM and HAM labels.")

    return messages, labels
