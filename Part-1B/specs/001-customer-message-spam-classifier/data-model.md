# Data Model: Customer Message Spam Classifier

## Customer Message

Represents one user submission to classify.

| Field  | Type   | Constraints                                                                                         |
| ------ | ------ | --------------------------------------------------------------------------------------------------- |
| `text` | string | Required; non-empty after trimming; English-language scope; never interpreted as executable content |

Invalid, missing, non-string, empty, or whitespace-only submissions are rejected
before prediction and do not produce a `Classification Result`.

## Classification Result

Represents a successful prediction for one valid message.

| Field        | Type        | Constraints                                                                                                                                                        |
| ------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `category`   | string enum | Exactly one of `SPAM`, `HAM`, `REVIEW`                                                                                                                             |
| `confidence` | number      | Finite numeric value in the inclusive range [0, 1]; maximum predicted probability estimate for SPAM or HAM, not a guaranteed calibrated probability of correctness |

The category is the predicted class when confidence is at least 0.70; otherwise it is
`REVIEW`. The 0.70 cutoff is a fixed design threshold, not a target REVIEW rate.
See [classification-result.schema.json](./contracts/classification-result.schema.json).

## Classification Error

Represents a rejected input or a processing failure, never a successful prediction.

| Field     | Type   | Constraints                                                                         |
| --------- | ------ | ----------------------------------------------------------------------------------- |
| `error`   | string | Stable, non-empty error code                                                        |
| `message` | string | Safe user-facing explanation; no stack trace, local path, or submitted message echo |

See [classification-error.schema.json](./contracts/classification-error.schema.json).

## Evaluation Case

Represents one fixed harness input and its expected outcome.
| Field | Type | Constraints |
|---|---|---|
| `case_id` | string | Unique and stable within the frozen evaluation manifest |
| `case_group` | string enum | Exactly one of `uci_held_out`, `synthetic_controlled`, `validation_only` |
| `scenario` | string enum | One of `normal`, `boundary`, `ambiguous`, `adversarial`, `missing`, `malformed` |
| `message` | any JSON value | English string for valid cases; missing or malformed JSON value for validation-only cases |
| `expected_label` | string or null | `SPAM` or `HAM` for valid labeled cases; null for validation-only cases |
| `expected_error` | string or null | Expected validation outcome for invalid cases; null for valid cases |
| `requirement_refs` | array of strings | At least one valid requirement or success-criterion ID identifying the behavior checked by the case |

The following field combinations are mandatory:
- For `uci_held_out` and `synthetic_controlled` cases, `scenario` MUST be one of `normal`, `boundary`, `ambiguous`, or `adversarial`; `message` MUST be a non-empty English string; `expected_label` MUST be exactly `SPAM` or `HAM`; and `expected_error` MUST be null.
- For `validation_only` cases, `scenario` MUST be `missing` or `malformed`; `expected_label` MUST be null; and `expected_error` MUST be a non-empty string identifying the expected validation error. A missing case MUST have no message value. A malformed case MUST contain a value that violates the valid-message input contract.
- No other combination of `case_group`, `scenario`, `message`, `expected_label`, and `expected_error` is valid.

The manifest contains at least 15 fixed valid labeled uci_held_out cases, with at
least five SPAM and five HAM cases. These UCI cases alone satisfy the minimum
classification-quality evaluation count. Required valid-message scenario coverage
(normal, boundary, ambiguous, and adversarial) must be represented across the
uci_held_out and synthetic_controlled groups. Synthetic/controlled cases may
supplement scenario and guardrail coverage but MUST NOT count toward the 15-case
minimum or classification-quality metrics. Missing and malformed cases belong to
the separate validation_only group and are not included in classification-quality
metrics. Keep the manifest separate from training data and from all fitting steps,
including TF-IDF fitting. Freeze its cases, labels, scenario coverage, and
acceptance criteria before final evaluation; do not edit them merely to improve
measured results.

## Evaluation Report

Reports independent outcomes for contract structure, invariants, and classification quality. All classification metrics (SPAM/HAM precision, recall, F1, macro-F1, REVIEW count, and REVIEW rate) MUST be calculated exclusively from cases whose case_group is uci_held_out. Synthetic/controlled cases and validation_only cases MUST NOT contribute. The total_valid_evaluation_case_count field counts only valid uci_held_out cases.

| Field                               | Type           | Constraints                                                                                                                                                                                                                                                 |
| ----------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `structural_validation_pass`        | boolean        | All applicable result/error objects satisfy their schemas; reported independently                                                                                                                                                                           |
| `invariant_validation_pass`         | boolean        | Confidence, category, threshold, and invalid-input rules hold; reported independently                                                                                                                                                                       |
| `evaluation_dataset_valid`          | boolean        | True only when the fixed evaluation dataset contains at least 15 valid uci_held_out cases, including at least five SPAM and five HAM cases, and meets required valid-message scenario coverage across uci_held_out and synthetic_controlled groups, label validity, required validation-case coverage, and separation from training and every fitting step |
| `classification_quality_pass`       | boolean        | True only when `evaluation_dataset_valid` is true and macro-F1 is at least 0.80; reported independently                                                                                                                                                     |
| `overall_pass`                      | boolean        | True only when structural validation, invariant validation, dataset validity, and classification-quality evaluation all pass                                                                                                                                |
| `failure_evidence`                  | array          | Structured, non-sensitive entries with `stage`, `code`, and `message` for each failure; empty when no failures occur                                                                                                                                        |
| `spam_precision`                    | number         | SPAM true positives divided by all cases predicted SPAM; in [0, 1]; REVIEW is not a predicted SPAM positive                                                                                                                                                 |
| `spam_recall`                       | number         | SPAM true positives divided by all SPAM-labeled cases; a REVIEW prediction for a true SPAM case is a false negative; in [0, 1]                                                                                                                              |
| `spam_f1`                           | number         | F1 derived from SPAM precision and recall; in [0, 1]                                                                                                                                                                                                        |
| `ham_precision`                     | number         | HAM true positives divided by all cases predicted HAM; in [0, 1]; REVIEW is not a predicted HAM positive                                                                                                                                                    |
| `ham_recall`                        | number         | HAM true positives divided by all HAM-labeled cases; a REVIEW prediction for a true HAM case is a false negative; in [0, 1]                                                                                                                                 |
| `ham_f1`                            | number         | F1 derived from HAM precision and recall; in [0, 1]                                                                                                                                                                                                         |
| `macro_f1`                          | number         | Arithmetic mean of SPAM F1 and HAM F1; REVIEW counts as incorrect for labeled SPAM/HAM cases                                                                                                                                                                |
| `review_count`                      | integer        | Number of valid evaluation cases categorized as REVIEW; at least 0 and no greater than `total_valid_evaluation_case_count`                                                                                                                                  |
| `review_rate`                       | number         | Equals `review_count / total_valid_evaluation_case_count` when the denominator is greater than 0; equals 0 when the denominator is 0; in [0, 1]; reports observed rate, not a target                                                                        |
| `total_valid_evaluation_case_count` | integer        | Denominator for classification metrics and REVIEW rate; at least 0 in a report; `evaluation_dataset_valid` requires at least 15 valid uci_held_out cases                                                                                                         |
| `human_decision`                    | string or null | Required field; `null` until a human reviewer decides; then exactly `ACCEPT` or `REJECT`; automation must never assign the decision                                                                                                                         |

`evaluation_dataset_valid` is true only when the frozen dataset has at least 15 valid
uci_held_out cases, including at least five true SPAM and five true HAM cases. These
UCI cases alone satisfy the minimum classification-quality evaluation count.
Required normal/boundary/ambiguous/adversarial valid-message scenario coverage
must be represented across uci_held_out and synthetic_controlled groups;
synthetic_controlled cases may supplement scenario and guardrail coverage but
MUST NOT count toward the 15-case minimum. The dataset must also have valid and
permitted labels, at least one separate missing case and one separate malformed
validation_only case, and no overlap with training data or any model/preprocessing
fitting step (including TF-IDF fitting).
Case IDs must be unique. Every case must have a permitted case_group and scenario
value, and a non-empty requirement_refs array whose entries each reference an
existing FR or SC ID. Every valid case must have exactly one SPAM/HAM label.
Otherwise it is false. Structural validation checks that this required field is a
boolean; invariant/property validation independently verifies that its value matches
the dataset and training manifest.

For each class, true positives are cases with that true label predicted as that
class. False negatives are all cases with that true label predicted as the other
class or REVIEW. False positives are cases with the other true label predicted as
that class. REVIEW predictions remain in the valid evaluation case denominator and
are false negatives for the true class; they are not silently dropped from recall
or quality scoring. REVIEW is not a predicted SPAM or HAM positive and therefore is
not counted as a positive prediction for either class's precision denominator.
Invalid-input validation cases are excluded from classification metrics and checked
separately by invariant/property validation.

When a class has no predicted positive cases, define its precision as 0. When a
class has no ground-truth positive cases in the dataset, define its recall as 0 and
mark the dataset invalid. When precision plus recall is 0, define that class's F1
as 0.
Macro-F1 is the arithmetic mean of SPAM F1 and HAM F1. The dataset validity rules
require both classes, so zero true cases must prevent classification-quality pass.

`classification_quality_pass` must be false whenever
`evaluation_dataset_valid` is false or macro-F1 is below 0.80. It may be true only
when the dataset is valid and macro-F1 is at least 0.80. `overall_pass` is true only
when structural validation, invariant/property validation, dataset validity, and
classification-quality evaluation all pass. These evaluation stages remain
independent and separately reported.

Each `failure_evidence` entry has a `stage` of `structural_validation`,
`invariant_validation`, `classification_quality`, or `runner`, a non-empty stable
failure `code`, and a non-empty concise `message`. It must not include submitted
message content, credentials, stack traces, or filesystem paths. The array is
empty when all stages pass. The harness runner aggregates component outcomes and
records each failure without assigning a human decision.

The following report-level invariants must be checked independently of JSON Schema
structural validation:

1. `review_count` must not exceed `total_valid_evaluation_case_count`.
2. When `total_valid_evaluation_case_count` is greater than zero,
   `review_rate` must equal
   `review_count / total_valid_evaluation_case_count`; when the denominator is
   zero, `review_rate` must equal 0.
3. `macro_f1` must equal the arithmetic mean of `spam_f1` and `ham_f1`.
4. `evaluation_dataset_valid` must match checks for minimum case count, class
   counts, scenario coverage, label validity, required validation cases, and
   training/evaluation separation.
5. `classification_quality_pass` may be true only when
   `evaluation_dataset_valid` is true and `macro_f1` is at least 0.80. Otherwise,
   it must be false.
6. `overall_pass` must be true only when all three independent validation stages
   pass, `evaluation_dataset_valid` is true, and `classification_quality_pass` is
   true.

The report must always include `human_decision`. It remains `null` until a human
reviewer makes a decision, then contains `ACCEPT` or `REJECT`. Automated structural,
invariant, and quality evaluation must never assign or infer this field.

Structural validation, invariant/property validation, and classification-quality
evaluation are independent checks with separate results. A failure in one check must
not be hidden by a pass in another. The report must not include raw submitted message
text or sensitive personal data. See
[evaluation-report.schema.json](./contracts/evaluation-report.schema.json).

## Relationships and lifecycle

- One valid `Customer Message` produces one `Classification Result`.
- An invalid `Customer Message` produces one `Classification Error` and no result.
- An `Evaluation Case` invokes the same classification behavior as a user
  submission.
- The frozen evaluation manifest produces an `Evaluation Report`; only a human may
  record final acceptance.

