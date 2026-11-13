# Implementation Plan: Customer Message Spam Classifier

**Branch**: `001-customer-message-spam-classifier` | **Date**: 2026-11-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-customer-message-spam-classifier/spec.md`

## Summary

Build a single-user English-language interface for classifying one customer message at a time as SPAM, HAM, or REVIEW. Use the specified TF-IDF and Multinomial Naive Bayes model, expose its highest class probability as confidence, and apply the confirmed 0.70 REVIEW cutoff. Provide a separate evaluator that checks the result contract, uncertainty and input guardrails, and per-class precision, recall, F1, macro-F1, REVIEW count, and REVIEW rate against fixed labeled evaluation cases.

Classifier confidence is a probability estimate, not a guarantee of correctness or a calibrated probability of correctness. The 0.70 cutoff is a fixed design threshold; the evaluator reports the observed REVIEW rate rather than treating the cutoff as a target rate.

The proposed Python-only interface is Streamlit. Keep the model and domain logic independent of the UI so the interface and evaluation harness exercise the same prediction behavior.

Use self-authored synthetic labeled SPAM/HAM messages for training and a separate self-authored synthetic held-out evaluation dataset. This approach follows the instructor's recommendation and avoids external dataset licensing and raw-corpus privacy concerns. The held-out evaluation dataset must contain at least 15 valid labeled cases, with at least five cases per class. These cases must remain separate from training and must not be used for model training, TF-IDF fitting, vocabulary construction, or any other data-fitting step. Include normal, boundary, ambiguous, and adversarial scenarios. Keep additional synthetic controlled cases separately identified and use them for supplemental scenario and guardrail checks. Keep missing and malformed cases in a separate validation-only group, checked for safe errors and excluded from macro-F1.

**## Technical Context**

**Language/Version**: Python 3.11 or later

**Primary Dependencies**: scikit-learn (TF-IDF and Multinomial Naive Bayes), Streamlit (single-message interface); pytest for automated tests

**Storage**: Local, versioned application configuration and evaluation metadata. Store self-authored synthetic training and evaluation datasets in their designated project locations. Keep training and held-out evaluation data separate. Do not include real customer messages, personal information, credentials, or other sensitive content in committed fixtures, logs, or evidence.

**Testing**: pytest unit, contract, and interface-flow tests; independent deterministic threshold-boundary unit tests at 0.699, 0.700, and 0.701; standalone evaluation command reporting structural, invariant/property, and classification-quality outcomes separately; a single `.harness/run_evaluation.py` runner aggregates results and writes `eval-results.json`.

**Target Platform**: Local Python environment with a browser for the Streamlit UI

**Project Type**: Single-project Python web application with a separately runnable evaluation harness

**Performance Goals**: Single-user local use; no throughput or availability SLA is defined in the specification

**Constraints**: English-only; TF-IDF + Multinomial Naive Bayes; confidence threshold 0.70; macro-F1 gate 0.80; self-authored synthetic training and held-out evaluation data; separate datasets with no evaluation leakage into model or TF-IDF fitting; minimum 15 valid labeled held-out evaluation cases with at least five per class; no execution of submitted message content.

**Scale/Scope**: One message per user submission, local single-user operation, at least 15 fixed labeled held-out evaluation messages (at least five per class), plus separate invalid-input cases

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- **Approved methods**: Pass. The planned classifier uses TF-IDF and Multinomial Naive Bayes, with no LLM or hardcoded message-pattern classifier.
- **Uncertainty and contract**: Pass. All valid-message predictions include a confidence score in [0, 1], and confidence below 0.70 yields REVIEW.
- **Evaluation integrity**: Pass by design. The synthetic training dataset is kept separate from fixed, labeled held-out evaluation cases; the evaluator independently checks output structure and invariants and reports macro-F1 against the fixed 0.80 gate.
- **Safety and privacy**: Pass by design. Submitted messages are inert text; logs omit message bodies; synthetic examples are self-authored, fictional, and reviewed before being committed.
- **Human decision**: Pass. Automated evaluation reports evidence but does not make the final ACCEPT/REJECT decision.
- **Data provenance and separation gate**: Self-authored synthetic messages are the selected data source. T004 remains a hard acceptance gate to document synthetic authorship, creation and labeling methods, dataset separation, scenario coverage, and privacy review before training or final evaluation. Do not bypass T004 for data-dependent work.

No constitutional exception is proposed. Re-check the data provenance and separation gate during task planning before implementation work that imports or packages message data.

## Project Structure

### Documentation (this feature)

```text
specs/001-customer-message-spam-classifier/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── classification-result.schema.json
│   ├── classification-error.schema.json
│   └── evaluation-report.schema.json
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml
README.md
app.py
src/
└── spam_classifier/
    ├── __init__.py
    ├── classifier.py
    ├── validation.py
    ├── data.py
    └── evaluation.py
tests/
├── unit/
│   ├── test_classifier.py
│   ├── test_review_threshold.py
│   ├── test_evaluation_metrics.py
│   └── test_validation.py
├── contract/
│   ├── test_result_contract.py
│   └── test_evaluation_report_contract.py
└── integration/
    ├── test_evaluation_harness.py
    └── test_app_flow.py
data/
└── README.md
evals/
└── dataset.json
.harness/
├── validate_structure.py
├── validate_invariants.py
├── evaluate_quality.py
├── run_evaluation.py
└── harness-log.md
eval-results.json
evidence/
├── initial-generation/
├── final-generation/
└── final-verification-transcript.txt
```

**Structure Decision**: Use one Python project, with prediction, input validation, data loading, metric calculation, and evaluation logic in an importable package. The Streamlit entry point stays at the repository root and calls the shared package.

Create separate self-authored synthetic training and held-out evaluation datasets. Keep `evals/dataset.json` separate from training. It must include at least 15 valid labeled synthetic held-out SPAM/HAM cases, with at least five per class, and cover normal, boundary, ambiguous, and adversarial scenarios. Identify supplemental synthetic controlled cases and validation-only missing/malformed cases separately, with unique IDs and requirement traceability. Only the fixed held-out quality cases contribute to macro-F1; supplemental controlled and validation-only cases receive their respective scenario or validation checks.

Keep the dataset authorship, creation method, labeling criteria, and privacy-review outcome documented. Do not use copied UCI messages or real customer messages as synthetic examples. Preserve the separation between training and evaluation, including TF-IDF fitting.

Keep structural contract checks, invariant/property checks, and classification-quality metric checks as separately reported `.harness/` components. The single harness runner invokes all three, aggregates their results, applies the fixed quality gate, and writes structured results and failure evidence. Preserve generation and verification evidence without exposing sensitive message content.

## Complexity Tracking

No constitutional violations or design exceptions are proposed. Self-authored synthetic data is the selected approach; dataset provenance, privacy review, and train/evaluation separation remain acceptance prerequisites.
