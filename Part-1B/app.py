"""Streamlit interface for the customer message spam classifier."""

from pathlib import Path

import streamlit as st

from spam_classifier.classifier import classify_message
from spam_classifier.classifier import train_model
from spam_classifier.validation import validate_message

ROOT = Path(__file__).resolve().parent
TRAINING_PATH = ROOT / "data" / "training.json"


@st.cache_resource
def load_model():
    """Train and cache the model using the approved training dataset."""
    return train_model(TRAINING_PATH)


st.set_page_config(
    page_title="Customer Message Spam Classifier",
)

st.title("Customer Message Spam Classifier")
st.caption("English messages only")

st.info(
    "Enter one English customer message to check whether it is "
    "SPAM, HAM, or requires REVIEW."
)

message = st.text_area(
    "Enter your customer message",
    max_chars=10000,
    placeholder="Type your message here...",
)

if st.button("Classify message"):
    try:
        validate_message(message)
        model = load_model()
        result = classify_message(model, message)

        st.subheader("Classification Result")

        category = result["category"]
        confidence = result["confidence"]

        if category == "SPAM":
            st.error("SPAM")
        elif category == "HAM":
            st.success("HAM")
        else:
            st.warning("REVIEW")

        st.write(f"Confidence: {confidence:.4f}")

        st.caption(
            "Confidence is the maximum predicted class probability estimate. "
            "It is not guaranteed to be a calibrated probability of correctness."
        )

    except ValueError as exc:
        safe_errors = {
            "Message is required.": "Message is required.",
            "Message must be text.": "Message must be text.",
            "Message cannot be empty.": "Message cannot be empty.",
        }
        st.error(safe_errors.get(str(exc), "The submitted message is invalid."))
    except Exception:
        st.error("The message could not be classified. Please try again.")
