# Part 1B - Harness Log

## 1. Evaluation Environment

- Python version: 3.11.0
- Test framework: pytest 8.4.2
- Application: Customer Message Spam Classifier
- Model: TF-IDF + Multinomial Naive Bayes
- Selected model parameter: `alpha=0.01`
- REVIEW threshold: 0.70
- Evaluation command: `python .\.harness\run_evaluation.py`
- Final evaluation date: 13 November 2026

## 2. Evaluation Criteria

- Structural validation: All output payloads must conform to the defined schemas.
- Invariant validation: Dataset and evaluation invariants must pass.
- Classification quality: Macro-F1 threshold is 0.80.
- Quality metrics: SPAM/HAM precision, recall, F1, and REVIEW rate.
- Quality metric scope: Only the 16 `synthetic_held_out` cases contribute to macro-F1. `synthetic_controlled` and `validation_only` cases are excluded.
- REVIEW predictions count as incorrect for held-out classification-quality metrics.
- Human decision: Must remain pending until manual review.

## 3. Initial Harness Run

- Structural validation: PASS
- Invariant validation: FAIL
- Evaluation dataset validation: FAIL
- Classification quality: FAIL
- Overall result: FAIL

### Initial Failure Evidence

- `MANIFEST_LOAD_FAILED`: Evaluation manifest could not be loaded or validated.
- `EVALUATION_DATASET_INVALID`: Manifest validation or training-data separation failed.
- `DATA_GATE_NOT_PASSED`: Quality evaluation was blocked because the T004 data gate had not passed.

### Initial Metrics

All metric values were zero because no approved evaluation dataset or predictions were available. These were not actual model-performance measurements.

- Human decision: Pending.

## 4. Data Approval and Repair

- Training data: 40 self-authored synthetic examples (20 SPAM, 20 HAM).
- Evaluation manifest: 22 self-authored synthetic cases.
- Held-out group: 16 cases (8 SPAM, 8 HAM).
- Controlled group: 4 cases.
- Validation-only group: 2 cases.
- Data provenance and manual review documented in `data/README.md`.
- Training and evaluation data manually reviewed and approved on 13 November 2026.
- T004 data gate: PASS.
- Data integrity hashes and manifest validation: PASS.
- Exact training/evaluation message overlap check: PASS.
- No held-out evaluation examples were used to fit the model.

## 5. Model Tuning and Repair

- Initial model: TF-IDF + Multinomial Naive Bayes with default `alpha`.
- Initial held-out macro-F1: 0.3838.
- Initial REVIEW count: 12 of 16.
- Diagnostic observation: The initial model predicted the expected underlying class for all 16 held-out cases, but 12 predictions fell below the 0.70 REVIEW threshold.
- Tuning method: 5-fold stratified cross-validation using only the 40 training examples.
- Candidate `alpha` values evaluated: 0.01, 0.05, 0.10, 0.30, 0.50, 1.00, 2.00, 5.00.
- Selected value: `alpha=0.01`.
- Selection basis: Highest threshold-adjusted cross-validation macro-F1 among the tested configurations.
- REVIEW threshold remained 0.70.
- Held-out dataset and labels were not changed during tuning.

## 6. Final Harness Run

- Evaluation date: 13 November 2026.
- Structural validation: PASS.
- Invariant validation: PASS.
- Evaluation dataset validation: PASS.
- Classification quality: PASS.
- Overall result: PASS.
- Failure evidence: None.

### Final Held-Out Metrics

- Held-out cases: 16.
- SPAM precision: 1.0000.
- SPAM recall: 1.0000.
- SPAM F1: 1.0000.
- HAM precision: 1.0000.
- HAM recall: 1.0000.
- HAM F1: 1.0000.
- Macro-F1: 1.0000.
- REVIEW count: 0.
- REVIEW rate: 0.0000.
- Required macro-F1: 0.80.
- Quality threshold: PASS.

## 7. Test Results

- Full automated test suite after model tuning: 156 passed.
- Evaluation harness integration tests: 6 passed.
- End-to-end harness: PASS.

## 8. Limitations and Human Review

- The training and evaluation examples are self-authored synthetic messages, not a representative sample of real customer communications.
- The held-out evaluation set contains only 16 cases.
- The perfect held-out score does not establish real-world generalization or calibrated confidence.
- Controlled and validation-only cases are not included in held-out macro-F1.
- The final automated report retains `human_decision: null`.
- Final human acceptance or rejection remains pending manual review.

