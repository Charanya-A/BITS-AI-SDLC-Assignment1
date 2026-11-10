# Quickstart: Customer Message Spam Classifier

This guide describes the planned local setup and acceptance checks. Commands become
executable after implementation and after a corpus passes the data-rights gate in
[research.md](./research.md).

## Prerequisites

- Python 3.11 or later
- A supported desktop browser
- UCI SMS Spam Collection v1, selected under CC BY 4.0, after the T004
  provenance, attribution, checksum, and privacy-safeguard gate is recorded

## Install

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The official [UCI record](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
identifies the dataset as CC BY 4.0 and credits Tiago Almeida and José Hidalgo.
Preserve academic attribution to the authors and the original dataset README's
attribution request and recommendation to contact them when using the corpus.
Complete T004 before using the corpus for project training or evaluation. Keep the downloaded
original archive outside Git and use only its label and message text. Normalize
messages consistently and deduplicate before partitioning unique normalized-message
groups; preserve class representation and ensure no normalized message is shared
between training and held-out evaluation. Build the quality-scoring portion of
`evals/dataset.json` from at least 15 deduplicated, privacy-reviewed, valid labeled
SPAM/HAM messages from the held-out UCI partition, with at least five per class and
no normalized message overlap with training or any fitting step, including TF-IDF.
Scenario coverage need not consist entirely of UCI messages: add separately
identified synthetic or controlled cases for ambiguous, adversarial, or boundary
scenario/guardrail checks where appropriate. Label them clearly as synthetic or
controlled; never represent them as UCI, and do not include them in the held-out UCI
macro-F1 calculation. Keep missing and malformed inputs in a separate
validation-only group; check them for safe validation errors and exclude them from
macro-F1. Preserve unique IDs, requirement traceability, frozen labels/scenarios,
and fixed evaluation criteria.

Pattern matches for email, phone-like text, and URLs are screening indicators only,
not confirmation of personal information or proof of anonymization. Exclude or
appropriately handle potential personal information in public fixtures. Do not put
raw phone numbers, email addresses, or other sensitive message content in committed
fixtures, logs, or evidence. Document residual privacy risks and automated-screening
limitations in `data/README.md`. Record the corpus version, source, license,
attribution, archive and extracted-file checksums, normalization/deduplication
policy, and split seed there.

## Run the interface

```powershell
streamlit run app.py
```

Submit an English message and verify the displayed category and confidence. Confidence
below 0.70 must display REVIEW; empty or malformed input must display a validation
error, not a prediction.

## Run automated tests and independent evaluation

```powershell
python -m pytest
python .harness/run_evaluation.py
```

The single harness runner must execute structural/schema validation,
invariant/property validation, and classification-quality evaluation as separate
components, aggregate their outcomes, apply the macro-F1 gate, and write the
structured report to `eval-results.json`. Classification quality must
include SPAM and HAM precision, recall, and F1 separately; macro-F1; REVIEW count and
rate; and total valid evaluation case count. REVIEW rate equals REVIEW count divided
by total valid evaluation case count when that count is greater than zero; when it is
zero, REVIEW rate is 0. It is reported, not optimized toward a target. The
classifier's confidence is a probability estimate and is not guaranteed to be
calibrated as a probability of correctness. The fixed 0.70 cutoff is a design
threshold.

The report's required `evaluation_dataset_valid` field is true only when the fixed
evaluation dataset in `evals/dataset.json` meets the minimum case count, class
counts, required scenario coverage, label validity, required missing/malformed
validation cases, and separation from training and every fitting step, including
TF-IDF.

The quality gate passes only at macro-F1 >= 0.80. Evaluation must fail if the fixed
manifest has fewer than 15 valid labeled cases, fewer than five examples for either
class, missing scenario coverage, or invalid-input cases treated as successful
predictions. Keep the fixed evaluation dataset separate from training and every fit
step, including TF-IDF. Do not change its cases, labels, criteria, or acceptance
threshold merely to improve the score.

A REVIEW prediction on a true SPAM or HAM case counts as a false negative for that
true class and remains in the valid-case denominator; it is not omitted from recall
or quality scoring. For zero division, precision is 0 when there are no predicted
positives, recall is 0 when there are no true positives, and F1 is 0 when precision
plus recall is 0. A missing true class makes the evaluation dataset invalid.

Run independent deterministic unit tests for the threshold decision: confidence
0.699 produces REVIEW, while 0.700 and 0.701 produce the predicted class. These
tests must use supplied boundary values rather than depending on model-generated
probabilities.

Do not bypass T004. The UCI dataset is the selected primary corpus under the
documented CC BY 4.0 license, subject to the project provenance, checksum,
attribution, and privacy safeguards. Do not commit the raw corpus or use evaluation
examples before the held-out privacy review.

## Expected end-to-end checks

1. A valid confident SPAM or HAM message returns the matching category and a finite
   confidence in [0, 1].
2. A valid message below the 0.70 threshold returns REVIEW.
3. Empty, whitespace-only, missing, or malformed input returns a safe validation
   error and no result object.
4. Text that looks like an instruction remains inert message content.
5. The evaluation run produces a reproducible `eval-results.json` report without
logging message bodies. Preserve initial-generation and final-generation snapshots
under `evidence/initial-generation/` and `evidence/final-generation/`, record actual
evaluation, failure, repair, and reevaluation events in `.harness/harness-log.md`,
and save the final verification transcript at
`evidence/final-verification-transcript.txt`. Do not fabricate evidence or record
repairs that did not occur. Automated evaluation must leave `human_decision` null.
