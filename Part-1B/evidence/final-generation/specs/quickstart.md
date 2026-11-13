# Quickstart: Customer Message Spam Classifier

This guide describes the local setup and acceptance checks for the Customer Message Spam Classifier. Complete the synthetic-data preparation and review requirements in T004 before training or classification-quality evaluation.

## Prerequisites

- Python 3.11 or later
- A supported desktop browser
- Self-authored synthetic English-language training data
- A separate, self-authored synthetic held-out evaluation dataset

Do not use copied UCI messages, other external corpus messages, or real customer messages as project training or evaluation examples.

## Install

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Prepare and review synthetic data

Complete T004 before training or classification-quality evaluation.

- Create original, fictional SPAM and HAM training examples in `data/training.json`.
- Create a separate fixed evaluation manifest at `evals/dataset.json`.
- Include at least 15 `synthetic_held_out` evaluation cases, with at least five SPAM and five HAM cases.
- Cover normal, boundary, ambiguous, and adversarial scenarios across the `synthetic_held_out` and `synthetic_controlled` groups.
- Keep missing and malformed inputs in the separate `validation_only` group.
- Do not count `synthetic_controlled` or `validation_only` cases toward the 15-case minimum or classification-quality metrics.
- Do not use held-out evaluation cases or labels for training, TF-IDF vocabulary fitting, preprocessing fitting, or model selection.
- Freeze evaluation cases, labels, scenario assignments, and acceptance criteria before final evaluation.

All examples must be original and fictional. Do not include real names, phone numbers, email addresses, URLs, credentials, or other personal or sensitive information.

Record the dataset authorship, label creation method, review method and outcome, group separation, scenario coverage, and privacy review in `data/README.md`. Do not mark T004 complete until the required datasets and documentation exist and have been reviewed.

## Run the interface

```powershell
streamlit run app.py
```

Submit an English message and verify the displayed category and confidence. Confidence below 0.70 must display REVIEW; empty or malformed input must display a validation error, not a prediction.

## Run automated tests and independent evaluation

```powershell
python -m pytest
python .harness/run_evaluation.py
```

The single harness runner must execute structural/schema validation, invariant/property validation, and classification-quality evaluation as separate components. It must aggregate their outcomes, apply the macro-F1 gate, and write the structured report to `eval-results.json`.

Classification quality must include SPAM and HAM precision, recall, and F1 separately; macro-F1; REVIEW count and rate; and total valid evaluation case count. These metrics must be calculated exclusively from `synthetic_held_out` cases.

REVIEW rate equals REVIEW count divided by total valid evaluation case count when that count is greater than zero. When it is zero, REVIEW rate is 0. It is reported, not optimized toward a target.

The classifier's confidence is a probability estimate and is not guaranteed to be calibrated as a probability of correctness. The fixed 0.70 cutoff is a design threshold.

The report's required `evaluation_dataset_valid` field is true only when the fixed evaluation dataset in `evals/dataset.json` meets all of the following:

- At least 15 valid `synthetic_held_out` cases.
- At least five SPAM and five HAM cases in that group.
- Required valid-message scenario coverage across `synthetic_held_out` and `synthetic_controlled`.
- Valid labels, unique case IDs, and requirement traceability.
- Separate missing and malformed `validation_only` cases.
- Documented synthetic authorship, label creation, and review.
- Separation from training data and every fitting step, including TF-IDF fitting.

The quality gate passes only at macro-F1 >= 0.80. Evaluation must fail if the fixed manifest has fewer than 15 valid held-out labeled cases, fewer than five examples for either class, missing scenario coverage, invalid labels, or invalid-input cases treated as successful predictions.

Keep the fixed evaluation dataset separate from training and every fitting step, including TF-IDF. Do not change its cases, labels, criteria, or acceptance threshold merely to improve the score.

A REVIEW prediction on a true SPAM or HAM case counts as a false negative for that true class and remains in the valid-case denominator; it is not omitted from recall or quality scoring.

For zero division:

- Precision is 0 when there are no predicted positives.
- Recall is 0 when there are no true positives.
- F1 is 0 when precision plus recall is 0.
- A missing true class makes the evaluation dataset invalid.

Run independent deterministic unit tests for the threshold decision: confidence 0.699 produces REVIEW, while 0.700 and 0.701 produce the predicted class. These tests must use supplied boundary values rather than depending on model-generated probabilities.

Do not bypass T004. Do not introduce external corpus data into the synthetic datasets. Do not claim classification-quality results until the actual model has been trained and evaluated against the frozen held-out manifest.

## Expected end-to-end checks

1. A valid confident SPAM or HAM message returns the matching category and a finite confidence in [0, 1].
2. A valid message below the 0.70 threshold returns REVIEW.
3. Empty, whitespace-only, missing, or malformed input returns a safe validation error and no result object.
4. Text that looks like an instruction remains inert message content.
5. The evaluation run produces a reproducible `eval-results.json` report without logging message bodies.
6. Preserve initial-generation and final-generation snapshots under `evidence/initial-generation/` and `evidence/final-generation/`.
7. Record actual evaluation, failure, repair, and reevaluation events in `.harness/harness-log.md`.
8. Save the final verification transcript at `evidence/final-verification-transcript.txt`.

Do not fabricate evidence or record repairs that did not occur. Automated evaluation must leave `human_decision` null. A human reviewer must make the final acceptance decision.
