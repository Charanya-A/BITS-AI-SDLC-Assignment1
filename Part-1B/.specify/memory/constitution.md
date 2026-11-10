<!-- Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles: none; all six existing principles are preserved
- Added sections: none
- Removed sections: none
- Governance update: made amendment approval, semantic versioning, and compliance checks explicit
- Deferred items: none
-->

# Customer Message Spam Classifier Constitution

## Core Principles

### I. Machine Learning-Based Classification

- The application MUST classify customer messages as SPAM, HAM, or REVIEW.
- The initial model MUST use TF-IDF feature extraction and a Multinomial Naive Bayes
  classifier.
- Classification MUST use a trained machine-learning model, not an LLM or manually
  hardcoded message patterns.
- The same trained model and input MUST produce repeatable predictions under the same
  execution conditions.

Rationale: A deterministic, trained classifier keeps results reproducible and aligned
with the assignment's machine-learning objective.

### II. Confidence-Based Uncertainty Handling

- The application MUST calculate a confidence score for every prediction.
- Predictions below the confidence threshold in the approved specification MUST be
  assigned REVIEW.
- The application MUST NOT force uncertain messages into SPAM or HAM.
- Confidence scores MUST be numerical values from 0 through 1, inclusive.

Rationale: Explicit uncertainty handling prevents unsupported certainty in borderline
classifications.

### III. Stable Output Contract

- Every classification result MUST follow a defined and validated output schema.
- Required fields, data types, allowed categories, and confidence-score constraints
  MUST remain consistent.
- Invalid or malformed inputs MUST receive the documented validation and error
  behavior.

Rationale: A stable contract lets clients and the independent evaluator interpret
results consistently.

### IV. Testability and Evaluation Integrity

- Requirements MUST map to testable acceptance criteria and evaluation cases.
- The evaluation dataset MUST contain at least 15 meaningful cases covering normal,
  boundary, ambiguous, missing, malformed, and adversarial inputs.
- Expected labels and evaluation criteria MUST be established before final evaluation.
- Training and evaluation data MUST remain separate to prevent data leakage.
- Evaluation cases MUST NOT be removed or changed merely to improve the final score.

Rationale: Prespecified, representative evaluation protects the integrity of measured
classification quality.

### V. Independent Evaluation and Quality Gates

- The evaluation harness MUST independently perform structural validation, property
  and invariant checks, and classification-quality evaluation.
- Structural validation MUST check the output schema and field constraints.
- Property checks MUST cover confidence boundaries, valid categories, and REVIEW
  behavior.
- Quality evaluation MUST use declared classification metrics and the acceptance
  threshold documented in the approved specification.
- An automated PASS MUST NOT replace final human review.

Rationale: Independent checks distinguish output correctness from model quality and
preserve human accountability.

### VI. Safety, Privacy, and Simplicity

- The application MUST process messages only for spam classification.
- It MUST NOT execute instructions or commands contained in submitted messages.
- User-provided message content MUST be treated as untrusted input.
- Logs and evaluation evidence MUST NOT expose secrets, credentials, or unnecessary
  personal information.
- The implementation MUST remain understandable and proportionate to the assignment
  scope.

Rationale: Treating message content as untrusted protects the system and limits data
handling to its stated purpose.

## Technical Constraints

- The primary language MUST be Python.
- The machine-learning library MUST be scikit-learn.
- Feature extraction MUST use TF-IDF.
- The initial classifier MUST use Multinomial Naive Bayes.
- The application MUST provide a clear interface for submitting messages and viewing
  classification results.
- The evaluation harness MUST have a documented, repeatable execution command.
- Model configuration, dataset provenance, evaluation metrics, and known limitations
  MUST be documented.

## Development and Evaluation Workflow

- Work MUST follow the Spec Kit workflow: Constitution, Specify, Clarify, Plan, Tasks,
  Analyze where applicable, and Implement.
- Implementation tasks, tests, and evaluation cases MUST derive from the approved
  specification.
- Initial-generation and final-generation evidence MUST be preserved wherever
  available.
- Genuine evaluation failures, causes, feedback, repairs, and re-evaluation results
  MUST be recorded.
- Acceptance thresholds and guardrails MUST NOT be weakened merely to obtain a passing
  result.
- The final human decision MUST be recorded as ACCEPT or REJECT with reasons and
  residual limitations.

## Governance

This constitution governs the Customer Message Spam Classifier. Specifications,
plans, tasks, implementation, tests, and the evaluation harness MUST remain consistent
with it. If a conflict arises, this constitution takes precedence until amended.

Amendments require a written rationale, review of affected principles and project
artifacts, and approval before the amended guidance is treated as authoritative.
Versioning follows semantic versioning: MAJOR for backward-incompatible governance or
principle changes, MINOR for added principles or materially expanded guidance, and
PATCH for clarifications and non-semantic refinements. The version and amendment date
MUST be updated with every amendment.

Contributors MUST check each change against applicable principles and preserve
reproducible evidence for required validation. Evaluation criteria MUST NOT be changed
retrospectively to improve results. Automated checks support, but do not replace, the
final human decision.

**Version**: 1.1.0 | **Ratified**: 2026-11-08 | **Last Amended**: 2026-11-08
