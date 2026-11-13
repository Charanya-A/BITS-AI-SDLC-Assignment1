"""Input validation for customer messages."""


def validate_message(message):
    """Validate one non-empty English customer message."""
    if message is None:
        raise ValueError("Message is required.")

    if not isinstance(message, str):
        raise ValueError("Message must be text.")

    if not message.strip():
        raise ValueError("Message cannot be empty.")

    return message.strip()
