# Implementation Plan: Customer Message Spam Classifier

**Branch**: `001-customer-message-spam-classifier` | **Date**: 2026-11-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-customer-message-spam-classifier/spec.md`

## Summary

Build a single-user English-language interface for classifying one customer message
at a time as SPAM, HAM, or REVIEW. Use the specified TF-IDF and Multinomial Naive
Bayes model, expose its highest class probability as confidence, and apply the
confirmed 0.70 REVIEW cutoff. Provide a separate evaluator that checks the result
contract, uncertainty and input guardrails, and per-class precision, recall, F1,
macro-F1, REVIEW count, and REVIEW rate against fixed labeled evaluation cases.
Classifier confidence is a probability estimate, not a guarantee of correctness or
a calibrated probability of correctness. The 0.70 cutoff is a fixed design
threshold; the evaluator reports the observed REVIEW rate rather than treating the
cutoff as a target rate.

The proposed Python-only interface is Streamlit. Keep the model and domain logic
independent of the UI so the interface and evaluation harness exercise the same
prediction behavior. Training and evaluation data must be separated. Use UCI SMS
Spam Collection v1 as the selected primary corpus under CC BY 4.0, with attribution
to Tiago Almeida and José Hidalgo and the original dataset README terms preserved.
T004 remains a hard gate for recording provenance, checksums, attribution, and
privacy safeguards before project use, training, or committing
evaluation examples. Keep the downloaded original corpus outside Git. Include at
least 15 deduplicated, privacy-reviewed held-out UCI valid labeled SPAM/HAM cases in
`evals/dataset.json`, with at least five per class. Supplemental synthetic or
controlled cases may cover ambiguous, adversarial, or boundary scenarios where
appropriate; mark them explicitly, never represent them as UCI, and use them for
scenario/guardrail checks rather than the held-out UCI macro-F1 calculation. Keep
missing and malformed cases in a separate validation-only group, checked for safe
errors and excluded from macro-F1.

## Technical Context

**Language/Version**: Python 3.11 or later

**Primary Dependencies**: scikit-learn (TF-IDF and Multinomial Naive Bayes),
Streamlit (single-message interface); pytest for automated tests

**Storage**: Local, versioned application configuration and evaluation metadata;
keep the downloaded original training corpus outside the Git repository. Keep
derived model artifacts local unless separately approved. Commit only held-out
evaluation examples that pass privacy review; do not expose raw phone numbers,
email addresses, or other sensitive content in fixtures, logs, or evidence.

**Testing**: pytest unit, contract, and interface-flow tests; independent deterministic
threshold-boundary unit tests at 0.699, 0.700, and 0.701; standalone evaluation
command reporting structural, invariant/property, and classification-quality
outcomes separately; a single `.harness/run_evaluation.py` runner aggregates results
and writes `eval-results.json`

**Target Platform**: Local Python environment with a browser for the Streamlit UI

**Project Type**: Single-project Python web application with a separately runnable
evaluation harness

**Performance Goals**: Single-user local use; no throughput or availability SLA is
defined in the specification

**Constraints**: English-only; TF-IDF + Multinomial Naive Bayes; confidence threshold
0.70; macro-F1 gate 0.80; selected UCI corpus under CC BY 4.0 with attribution;
T004 rights/provenance/privacy gate; normalize and deduplicate before deterministic
group splitting; held-out evaluation examples must pass privacy review; no execution
of submitted message content

**Scale/Scope**: One message per user submission, local single-user operation, at
least 15 fixed labeled evaluation messages (at least five per class), plus invalid
input cases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Approved methods**: Pass. The planned classifier uses TF-IDF and Multinomial
  Naive Bayes, with no LLM or hardcoded message-pattern classifier.
- **Uncertainty and contract**: Pass. All valid-message predictions include a
  confidence score in [0, 1], and confidence below 0.70 yields REVIEW.
- **Evaluation integrity**: Pass by design. The training corpus is kept separate
  from fixed, labeled evaluation cases; the evaluator independently checks output
  structure and invariants and reports macro-F1 against the fixed 0.80 gate.
- **Safety and privacy**: Pass by design. Submitted messages are inert text; logs
  omit message bodies; dataset use is gated on an explicit compatible license and
  privacy review.
- **Human decision**: Pass. Automated evaluation reports evidence but does not make
  the final ACCEPT/REJECT decision.
- **Data-rights/provenance/privacy gate**: UCI SMS Spam Collection v1 is the selected
  primary dataset; the reviewed UCI record identifies CC BY 4.0 and the authors.
  T004 remains a hard acceptance gate to record those terms and attribution, verify
  the reviewed hashes, keep the raw archive outside Git, and enforce held-out
  evaluation-example privacy review before committing examples. Potential personal
  information pattern matches are screening indicators, not proof of identity or
  anonymization. Do not bypass T004 for dataset use, training, or committing
  evaluation examples.

No constitutional exception is proposed. Re-check the data-rights gate during task
planning before implementation work that imports or packages message data.

## Project Structure

### Documentation (this feature)

```text
specs/001-customer-message-spam-classifier/
â”œâ”€â”€ plan.md
â”œâ”€â”€ research.md
â”œâ”€â”€ data-model.md
â”œâ”€â”€ quickstart.md
â”œâ”€â”€ contracts/
â”‚   â”œâ”€â”€ classification-result.schema.json
â”‚   â”œâ”€â”€ classification-error.schema.json
â”‚   â””â”€â”€ evaluation-report.schema.json
â””â”€â”€ tasks.md
```

### Source Code (repository root)

```text
pyproject.toml
README.md
app.py
src/
â””â”€â”€ spam_classifier/
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ classifier.py
    â”œâ”€â”€ validation.py
    â”œâ”€â”€ data.py
    â””â”€â”€ evaluation.py
tests/
â”œâ”€â”€ unit/
â”‚   â”œâ”€â”€ test_classifier.py
â”‚   â”œâ”€â”€ test_review_threshold.py
â”‚   â”œâ”€â”€ test_evaluation_metrics.py
â”‚   â””â”€â”€ test_validation.py
â”œâ”€â”€ contract/
â”‚   â”œâ”€â”€ test_result_contract.py
â”‚   â””â”€â”€ test_evaluation_report_contract.py
â””â”€â”€ integration/
    â”œâ”€â”€ test_evaluation_harness.py
    â””â”€â”€ test_app_flow.py
data/
â””â”€â”€ README.md
evals/
â””â”€â”€ dataset.json
.harness/
â”œâ”€â”€ validate_structure.py
â”œâ”€â”€ validate_invariants.py
â”œâ”€â”€ evaluate_quality.py
â”œâ”€â”€ run_evaluation.py
â””â”€â”€ harness-log.md
eval-results.json
evidence/
â”œâ”€â”€ initial-generation/
â”œâ”€â”€ final-generation/
â””â”€â”€ final-verification-transcript.txt
```

**Structure Decision**: Use one Python project, with prediction, input validation,
data loading, metric calculation, and evaluation logic in an importable package. The
Streamlit entry point stays at the repository root and calls the shared package.
Normalize and deduplicate the corpus before deterministic group-level partitioning,
preserve class representation, and keep held-out examples out of all fitting,
including TF-IDF. Keep `evals/dataset.json` separate from training. It must include
the minimum held-out UCI set for quality evaluation, while separately identifying
supplemental synthetic/controlled cases and validation-only missing/malformed
cases, with unique IDs and requirement traceability. Synthetic cases must never be
represented as UCI and are used for separate scenario/guardrail checks, not
held-out UCI macro-F1 scoring; invalid-input cases receive validation checks, not
macro-F1 scoring. Include only UCI examples that
pass privacy review. Keep the downloaded original corpus outside Git; do not commit
raw messages. Keep structural contract checks,
invariant/property checks, and classification-quality metric checks as separately
reported `.harness/` components. The single harness runner invokes all three,
aggregates their results, applies the fixed quality gate, and writes structured
results and failure evidence. Preserve generation and verification evidence without
exposing sensitive message content.

## Complexity Tracking

No constitutional violations or design exceptions are proposed. Dataset rights are a
release prerequisite, not a waived requirement.
