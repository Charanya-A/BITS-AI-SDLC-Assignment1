# Customer Message Spam Classifier

A local, single-user application that classifies one English customer message at a time as SPAM, HAM, or REVIEW.

## Technology

- Python 3.11+
- scikit-learn: TF-IDF and Multinomial Naive Bayes
- Streamlit: local user interface
- pytest: automated tests

## Setup

Create and activate a virtual environment:

    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install -e ".[dev]"

## Running the application

    streamlit run app.py

## Running tests

Run the complete test suite:

    python -m pytest

Run the evaluation harness:

    python .\.harness\run_evaluation.py

Run the data gate independently:

    python .\.harness\validate_data_gate.py

## Data provenance and handling

The training and evaluation datasets are self-authored synthetic examples. No external message corpus is used for model training or classification-quality evaluation.

The training dataset contains 40 manually authored messages:

- 20 SPAM
- 20 HAM

The evaluation manifest contains 22 manually authored cases:

- 16 synthetic held-out classification-quality cases (8 SPAM and 8 HAM)
- 4 synthetic controlled cases
- 2 validation-only cases

Training and evaluation examples are kept separate. Only the 16 held-out cases contribute to classification-quality metrics. Controlled and validation-only cases are excluded from macro-F1.

The examples were manually reviewed and approved on 13 November 2026. Dataset provenance, review, privacy checks, and integrity information are documented in `data/README.md`.

Do not add external or personal customer messages without reviewing their rights, provenance, privacy implications, and the project's data requirements.

## Classification behavior

The application uses a TF-IDF feature representation and a Multinomial Naive Bayes classifier.

The predicted class is SPAM or HAM. The application returns REVIEW when the maximum predicted class probability estimate is below 0.70. At or above 0.70, it returns the predicted class.

The confidence value is the model's maximum class-probability estimate. It is not a guarantee that the prediction is correct or that the probability is calibrated.

## Evaluation

The evaluation harness validates project structure, invariants, the evaluation dataset, and classification quality.

The classification-quality threshold is a held-out macro-F1 of at least 0.80. REVIEW predictions count as incorrect for the held-out classification-quality calculation.

Latest recorded evaluation:

- Held-out cases: 16
- SPAM precision: 1.00
- SPAM recall: 1.00
- HAM precision: 1.00
- HAM recall: 1.00
- Macro-F1: 1.00
- REVIEW count: 0
- Overall harness result: PASS

These results apply only to the small, self-authored synthetic evaluation set. They do not establish real-world performance, generalization to actual customer messages, or calibrated confidence.

## Human review

An automated PASS is not a human acceptance decision. The final `human_decision` remains null until the project is reviewed and an explicit ACCEPT or REJECT decision is recorded.

## Project limitations

- English-language messages only.
- Local, single-user application.
- Small, self-authored synthetic datasets.
- No claim of real-world generalization.
- Confidence estimates are not guaranteed to be calibrated.
