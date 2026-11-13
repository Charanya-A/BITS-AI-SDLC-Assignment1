# Tasks: Customer Message Spam Classifier

**Input**: Design documents from `/specs/001-customer-message-spam-classifier/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`

**Tests**: Included because the constitution requires automated tests and the approved specification requires an independent evaluation harness.

**Organization**: Tasks are ordered by shared setup and foundational prerequisites, then by the three independently testable user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tasks can run in parallel because they edit different files and have no dependency on unfinished work.
- **[Story]**: User-story label for tasks in story phases.
- Every task names the implementation or test file it changes.

## Phase 1: Setup

**Purpose**: Initialize the Python project and its planned package/test structure.

- [x] T001 Define Python 3.11+ runtime and scikit-learn, Streamlit, and pytest development dependencies in `pyproject.toml`.
- [x] T002 [P] Create the importable package and test directory skeleton listed in `specs/001-customer-message-spam-classifier/plan.md` using `src/spam_classifier/__init__.py` and `tests/`.
- [x] T003 [P] Create project setup, synthetic-data provenance, and local-data handling guidance in `README.md` and `data/README.md`; state that only self-authored synthetic examples may be used and that training and held-out evaluation data must remain separate.

## Phase 2: Foundational

**Purpose**: Establish synthetic-data provenance, shared validation, reporting, and test foundations.

- [ ] T004 Create and review self-authored synthetic SPAM/HAM training data in `data/training.json` and document its authorship, label creation method, review method and outcome, and privacy safeguards in `data/README.md`. Create the separate held-out evaluation data required by T025 only after its cases and labels have been authored and reviewed. Confirm that all examples are original and fictional, contain no real personal or sensitive information, and are not copied from UCI or another external corpus. Document the separation between training and held-out evaluation data and confirm that held-out examples are not used for training, TF-IDF fitting, preprocessing fitting, or model selection. This remains a hard data-readiness gate before model training or classification-quality evaluation. Do not mark complete until the required artifacts and documentation exist and have been reviewed.

- [x] T005 [P] Create shared test fixtures and deterministic confidence-result helpers for unit and contract tests in `tests/conftest.py`; do not load or fit a corpus in shared fixtures.
- [x] T006 [P] Configure the project's pytest discovery and test paths in `pyproject.toml` so unit, contract, and integration tests can be run independently and together.

**Checkpoint**: Data-dependent model training and classification-quality evaluation may begin only after T004's synthetic-data requirements and T025's held-out evaluation dataset requirements are satisfied. Data-independent work and tests may continue before then.

## Phase 3: User Story 1 - Classify a Message (Priority: P1)

**Goal**: Submit one English message and display SPAM, HAM, or REVIEW with its confidence estimate.

**Independent Test**: With the reviewed synthetic training data available, run the local interface and submit valid English messages. Verify result category, confidence bounds, and the 0.70 REVIEW threshold.

### Tests for User Story 1

- [x] T007 [P] [US1] Add deterministic unit tests in `tests/unit/test_review_threshold.py` proving confidence 0.699 returns REVIEW and 0.700 and 0.701 return the predicted class, using supplied confidence values without fitting a model or loading a corpus.
- [x] T008 [P] [US1] Add classifier unit tests in `tests/unit/test_classifier.py` for English valid input, allowed result categories, finite confidence in [0, 1], repeatability for a fixed fitted model, and maximum-class-probability confidence.
- [x] T009 [P] [US1] Add result schema contract tests in `tests/contract/test_result_contract.py` using `specs/001-customer-message-spam-classifier/contracts/classification-result.schema.json` and assert exactly `category` and `confidence` are returned.

### Implementation for User Story 1

- [x] T010 [US1] Implement a pure confidence-threshold decision helper in `src/spam_classifier/classifier.py` that returns REVIEW only below 0.70 and otherwise returns the predicted class, so supplied boundary values can be tested independently.
- [ ] T011 [US1] After T004 passes, implement synthetic training-data loading and validation in `src/spam_classifier/data.py`; load only original self-authored synthetic SPAM/HAM examples from `data/training.json`, validate labels and message content, and ensure the held-out evaluation manifest is never loaded into the training or fitting path.
- [ ] T012 [US1] Implement the TF-IDF and Multinomial Naive Bayes training and prediction pipeline in `src/spam_classifier/classifier.py`; fit the vectorizer and classifier using only the synthetic training data, derive confidence from the maximum predicted class probability estimate, use the T010 threshold helper, and document that confidence is not guaranteed calibrated probability of correctness.
- [ ] T013 [US1] Implement the single-message Streamlit interface in `app.py` to accept one English message and display its SPAM, HAM, or REVIEW category and confidence; clearly state English-only support.

**Checkpoint**: User Story 1 works independently when the synthetic training data has passed T004 review and the model pipeline is implemented.

## Phase 4: User Story 2 - Handle Uncertain or Invalid Messages Safely (Priority: P2)

**Goal**: Reject invalid submissions clearly, preserve REVIEW behavior for uncertain messages, and treat adversarial content only as inert text.

**Independent Test**: Submit empty, whitespace-only, missing, non-text, malformed, ambiguous, and instruction-like input. Verify validation errors are distinct from predictions, low-confidence valid messages return REVIEW, and no submitted content is executed or echoed in logs or errors.

### Tests for User Story 2

- [x] T014 [P] [US2] Add input validation tests in `tests/unit/test_validation.py` for missing, non-string, empty, whitespace-only, and malformed message input; assert each rejected input produces no classification result.
- [x] T015 [P] [US2] Add safety and UI flow tests in `tests/integration/test_app_flow.py` for ambiguous low-confidence text, instruction-like inert text, clear English-only notice, and errors distinct from successful result display.
- [x] T016 [P] [US2] Add error response schema tests in `tests/contract/test_error_contract.py` using `specs/001-customer-message-spam-classifier/contracts/classification-error.schema.json`; assert errors are non-empty and contain no stack trace, local path, or submitted message echo.

### Implementation for User Story 2

- [x] T017 [US2] Implement message input validation in `src/spam_classifier/validation.py` for missing, non-string, empty, and whitespace-only input; return documented safe errors and never create a prediction for invalid input.
- [x] T018 [US2] Update `app.py` to display validation errors separately from classification results and to treat all submitted message content as inert text.
- [x] T019 [US2] Ensure logging and error handling in `src/spam_classifier/validation.py` and `app.py` omit message bodies, credentials, stack traces, and filesystem paths.

**Checkpoint**: User Stories 1 and 2 work independently; invalid input never appears as a successful result.

## Phase 5: User Story 3 - Evaluate Classification Quality (Priority: P3)

**Goal**: Run an independent evaluator that separately reports structural validation, invariant/property validation, and classification-quality metrics on a fixed self-authored synthetic evaluation set.

**Independent Test**: Run the evaluation command and verify dataset requirements, report schema, report invariants, per-class metrics, REVIEW statistics, and the fixed macro-F1 >= 0.80 gate. Confirm automated checks leave `human_decision` null.

### Tests for User Story 3

- [x] T020 [P] [US3] Add fixed-case manifest validation tests in `tests/unit/test_evaluation_manifest.py` using data-independent fixtures that distinguish at least 15 valid, labeled `synthetic_held_out` cases (at least five SPAM and five HAM) from separately identified `synthetic_controlled` scenario fixtures and at least one separate `missing` and one separate `malformed` `validation_only` case; verify normal/boundary/ambiguous/adversarial coverage, valid `case_group` values and non-empty, valid `requirement_refs`; reject invalid cross-field combinations, including invalid group/scenario and label/error combinations; and exclude invalid-input cases from classification metrics. Do not treat fixtures as the frozen evaluation dataset.
- [x] T021 [P] [US3] Add metric calculation tests in `tests/unit/test_evaluation_metrics.py` for SPAM and HAM precision, recall, and F1, macro-F1 as the arithmetic mean of class F1 values, REVIEW count/rate, and total valid-case count; count REVIEW as a false negative for the true class and keep it in class recall denominators; test zero-predicted-positive precision as 0, zero-ground-truth-positive recall as 0 with an invalid dataset, and zero-sum precision/recall F1 as 0.
- [x] T022 [P] [US3] Add report-level invariant tests in `tests/unit/test_evaluation_invariants.py` asserting `review_count <= total_valid_evaluation_case_count`; `review_rate == review_count / total_valid_evaluation_case_count` when the denominator is greater than zero and `review_rate == 0` when it is zero; `macro_f1 == (spam_f1 + ham_f1) / 2`; `classification_quality_pass` is true only when the evaluation dataset is valid and macro-F1 is at least 0.80; and `overall_pass` is true only when every required validation stage and the quality gate pass.
- [x] T023 [P] [US3] Add evaluation report schema and zero-case report tests in `tests/contract/test_evaluation_report_contract.py` against `specs/001-customer-message-spam-classifier/contracts/evaluation-report.schema.json`; assert every required report field is present, including `evaluation_dataset_valid`, `overall_pass`, and `failure_evidence`, and `human_decision` is null until a human review. Add a zero-valid-case failure-report fixture that asserts `review_rate` is exactly 0 without division by zero, `evaluation_dataset_valid` is false, and `classification_quality_pass` is false.
- [x] T024 [P] [US3] Add evaluator integration tests in `tests/integration/test_evaluation_harness.py` proving structural, invariant/property, and classification-quality outcomes are reported independently and automated evaluation never assigns `ACCEPT` or `REJECT`.

### Implementation for User Story 3

- [ ] T025 [US3] Create and freeze `evals/dataset.json` with at least 15 original, self-authored synthetic `synthetic_held_out` SPAM/HAM cases, at least five per class, unique `case_id` values, and no message overlap with training data or any fitting step, including TF-IDF. Include normal, boundary, ambiguous, and adversarial scenario coverage across `synthetic_held_out` and separately identified `synthetic_controlled` cases. Include at least one separate `validation_only` case with scenario `missing` and no `message`, and at least one separate `validation_only` case with scenario `malformed` and a value violating the valid-message input contract. Preserve labels, `requirement_refs` entries per case referencing existing FR or SC IDs, and fixed evaluation criteria. All examples must be original, fictional, and free of real personal or sensitive information. Document authorship, label creation, review, group separation, and scenario coverage in `data/README.md`. Do not change cases or criteria to improve scores.
- [ ] T026 [US3] Implement fixed evaluation manifest loading and validity checks in `src/spam_classifier/evaluation.py`; distinguish `synthetic_held_out` quality cases, separately marked `synthetic_controlled` scenario cases, and invalid-input `validation_only` cases. Set `evaluation_dataset_valid` only when at least 15 valid `synthetic_held_out` cases are present, including at least five per class, required scenario coverage is represented across the valid case groups, `case_id` values are unique, valid case combinations are enforced: `synthetic_held_out` and `synthetic_controlled` cases MUST use a valid-message scenario (`normal`, `boundary`, `ambiguous`, or `adversarial`), a non-empty English message, exactly one `SPAM` or `HAM` expected label, and null `expected_error`; `validation_only` cases MUST use `missing` or `malformed`, have a null expected label, and a non-empty expected error, with missing messages absent and malformed messages violating the input contract. The manifest MUST contain at least one separate `missing` validation-only case and at least one separate `malformed` validation-only case. No other combination is valid. Every case MUST also have a non-empty `requirement_refs` array whose entries reference existing FR or SC IDs. Validate documented synthetic provenance and separation from training and every fitting step; reject violations without changing frozen cases or criteria.
- [x] T027 [US3] Implement SPAM/HAM precision, recall, F1, macro-F1, REVIEW count/rate, and total valid-case count calculations in `src/spam_classifier/evaluation.py` using only the fixed labeled `synthetic_held_out` quality cases; exclude `synthetic_controlled` guardrail cases and `validation_only` cases from held-out macro-F1, and count REVIEW as incorrect for labeled synthetic SPAM/HAM cases.
- [x] T028 [US3] Implement evaluator-level report invariants in `src/spam_classifier/evaluation.py` independently of schema validation and metric calculation, explicitly testing `review_count <= total_valid_evaluation_case_count`, `review_rate == review_count / total_valid_evaluation_case_count` when the denominator is greater than zero and `review_rate == 0` when it is zero, macro-F1 equal to the arithmetic mean of SPAM and HAM F1, `evaluation_dataset_valid` matching the manifest/training evidence, `classification_quality_pass` false for an invalid dataset and true only when a valid dataset has macro-F1 >= 0.80, and human-owned `human_decision`.
- [x] T029 [US3] Implement structural/schema validation as a separate `.harness/validate_structure.py` component that validates result and evaluation report payloads against their JSON schemas, reports its own outcome, and emits structured failure evidence without performing invariant or quality scoring.
- [x] T030 [US3] Implement invariant/property validation as a separate `.harness/validate_invariants.py` component that checks classification and report invariants, dataset validity, and that automated evaluation leaves `human_decision` null; report its outcome and structured failures separately from schema and quality validation.
- [ ] T031 [US3] Implement classification-quality evaluation as a separate `.harness/evaluate_quality.py` component that calculates the defined SPAM/HAM metrics, REVIEW statistics, valid-case count, macro-F1, and fixed 0.80 gate from the frozen labeled `synthetic_held_out` cases only; do not include supplemental `synthetic_controlled` cases or `validation_only` cases in macro-F1, and do not change cases or criteria.
- [ ] T032 [US3] Implement one repeatable full-pipeline runner in `.harness/run_evaluation.py` that invokes the three independent harness components, aggregates all outcomes, applies the fixed quality gate, leaves `human_decision` null, writes the complete structured report and stage-specific failure evidence to root `eval-results.json`, and exits nonzero when any required stage fails.

**Checkpoint**: The fixed synthetic dataset is valid and isolated from all training and fitting steps; the single harness runner executes and aggregates structural validation, invariant/property validation, and classification-quality evaluation separately, writes `eval-results.json` with structured failure evidence, and leaves the human decision unassigned.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify documentation, security, reproducibility, and final acceptance evidence across all stories.

- [ ] T033 Update `README.md` and `data/README.md` with synthetic-data authorship and provenance, label creation and review methods, training/evaluation separation, privacy safeguards and review limitations, model limitations, confidence-estimate caveat, fixed-threshold behavior, observed REVIEW rate, and reproducible training/evaluation commands.
- [ ] T034 Create and populate `evidence/initial-generation/` with actual initial-generation artifacts and provenance metadata; do not fabricate snapshots or include external or sensitive message content.
- [ ] T035 After implementation and evaluation, create and populate `evidence/final-generation/` with actual final-generation artifacts and provenance metadata; do not fabricate snapshots or include external or sensitive message content.
- [ ] T036 Create and maintain `.harness/harness-log.md` with actual model/configuration details, predeclared threshold and scoring method, actual runs and failures, and repair/reevaluation evidence only when they occurred; leave final human review for T040 and do not fabricate or imply uneventful runs.
- [ ] T037 Generate and retain root `eval-results.json` from the repeatable full-pipeline runner, including actual stage outcomes, metrics, `evaluation_dataset_valid`, and structured failure evidence; automated evaluation must leave `human_decision` null.
- [ ] T038 Run all commands and end-to-end scenarios in `specs/001-customer-message-spam-classifier/quickstart.md`; record actual outputs, failures, repairs, and rerun outcomes in `evidence/final-verification-transcript.txt`.
- [ ] T039 Review `src/spam_classifier/`, `app.py`, `data/`, and `evals/dataset.json` against the constitution for secrets, exposed personal information, executed message content, changed evaluation criteria, copied external corpus content, shared messages across training and held-out partitions, or training/evaluation data used before T004; document actual privacy-review limitations and findings in `evidence/final-verification-transcript.txt`.
- [ ] T040 Record the final human ACCEPT or REJECT decision and rationale in `evidence/final-verification-transcript.txt` and `.harness/harness-log.md`; do not derive or assign this decision from automated PASS results.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on project setup. T004 is a hard prerequisite for model training and classification-quality evaluation.
- **User Stories (Phases 3-5)**: Depend on shared setup. Data-dependent portions additionally require T004 and the relevant dataset artifacts; do not bypass the synthetic-data review gate.
- **Polish (Phase 6)**: Depends on the desired stories and their validation being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on setup and reviewed synthetic training data before model fitting; pure threshold logic/tests can be developed independently.
- **User Story 2 (P2)**: Depends on setup; UI integration uses User Story 1's result behavior.
- **User Story 3 (P3)**: Depends on setup and a frozen, reviewed synthetic evaluation dataset before classification-quality evaluation; evaluation consumes the classification result behavior from User Story 1 and input/error behavior from User Story 2.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001 establishes the project layout.
- T005 and T006 can run in parallel after setup; neither task may load or fit project data.
- T007, T008, and T009 can be authored in parallel; independent threshold tests do not need a dataset.
- T014, T015, and T016 can be authored in parallel.
- T020 through T024 can be authored in parallel because they target separate test concerns; keep report-field expectations consistent with the shared schema.
- T029 can be implemented independently after the report schemas are finalized. T030 follows T026 and T028; T031 follows T027. T032 depends on all three components.
- T033 can be completed after synthetic-data authorship and evaluation policy are documented; document any unresolved data gate rather than claiming it passed.
- T034 requires actual initial-generation artifacts. T035 requires implementation and evaluation to be complete. T036 is maintained as actual runs occur; T037 requires the runner to be complete. T038-T039 require implementation to be complete, and T040 requires T036-T039 and the final human review.

### Task-Level Dependencies

- T011 requires T004 to pass; T012 requires T010, T011, and reviewed training data; T013 requires T012.
- T018 requires T013 and T017; T019 requires T017 and T018.
- T025 requires T004; T026 and T027 require the frozen manifest from T025; T028 requires T026 and T027.
- T029 requires the finalized report schemas. T030 requires T026 and T028; T031 requires T027. T032 requires T029, T030, and T031.
- T037 requires T032. T038 requires T032 and T037, then runs the quickstart pipeline; T039 reviews the completed implementation. T040 records the final human decision after T036-T039; automated outputs remain unchanged.

## Parallel Example: User Story 1

```text
After setup, author T007 threshold tests, T008 classifier tests, and T009
result-contract tests in parallel. Implement the pure threshold helper before
running T007. Model training must wait until the synthetic training data has
passed T004 review.
```

## Parallel Example: User Story 3

```text
Author T020-T024 tests in parallel; these data-independent tests must not load
or acquire an external corpus. Complete T004 and create and freeze the synthetic
evaluation manifest before classification-quality evaluation.
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete setup and review the self-authored synthetic training data.
2. Implement and independently test the threshold helper at 0.699, 0.700, and 0.701.
3. Fit TF-IDF and Multinomial Naive Bayes on the training data only.
4. Deliver the single-message UI and verify category/confidence behavior.

### Incremental Delivery

1. Complete setup and synthetic-data review.
2. Deliver User Story 1 and validate the classification flow.
3. Add User Story 2 and validate invalid, uncertain, and adversarial input behavior.
4. Freeze a separate synthetic evaluation dataset and deliver User Story 3's independent structural, invariant/property, and quality checks.
5. Complete cross-cutting security, documentation, and human acceptance evidence.

The initial and final generation evidence, harness log, evaluation report, and final verification transcript must capture actual events and outputs. A failed or incomplete data-review gate blocks model training and classification-quality evaluation; threshold-helper work and data-independent tests may continue.

Do not lower the macro-F1 gate, alter fixed evaluation criteria, or use copied external corpus messages to produce a passing result.
