# Dataset Documentation

## 1. Data Sources and Authorship

This project uses synthetic examples created specifically for the Customer Message Spam Classifier assignment with AI assistance. The examples were manually reviewed and approved by the project author.

No UCI SMS Spam Collection messages, external datasets, customer messages, or real personal communications were used.

## 2. Training Dataset

File: `data/training.json`

- Total examples: 40
- SPAM: 20
- HAM: 20
- All examples contain a message and its assigned label.
- The training examples are separate from the held-out evaluation cases.

## 3. Evaluation Dataset

File: `evals/dataset.json`

| Group                | Total | SPAM | HAM |
| -------------------- | ----: | ---: | --: |
| synthetic_held_out   |    16 |    8 |   8 |
| synthetic_controlled |     4 |    2 |   2 |
| validation_only      |     2 |  N/A | N/A |

The held-out set covers normal, boundary, ambiguous, and adversarial scenarios.

The controlled cases provide additional scenario and guardrail coverage. Validation-only cases cover missing and malformed inputs.

Only `synthetic_held_out` cases contribute to classification-quality metrics. Controlled and validation-only cases are excluded.

## 4. Labeling and Review Method

Labels were assigned according to message intent:

- SPAM: unsolicited promotional, deceptive, suspicious reward, or misleading solicitation.
- HAM: ordinary personal, transactional, educational, or workplace communication.

The project author reviewed the training examples and approved their labels. The project author also reviewed the evaluation messages, scenarios, and expected labels and approved the manifest.

Review outcome: Approved.

Review date: 2026-11-13.

## 5. Data Separation

- Training examples are used to fit the classifier and its TF-IDF vocabulary.
- Held-out evaluation examples are kept separate from model and vocabulary fitting.
- Held-out labels are used only for evaluation.
- Controlled and validation-only cases are not included in held-out macro-F1 calculations.
- The held-out manifest must remain unchanged during model development and evaluation unless an objectively identified data error requires a documented correction.

## 6. Privacy and Safety

The datasets contain fictional synthetic messages. They do not intentionally include real names, phone numbers, email addresses, URLs, passwords, API keys, credentials, or customer information.

No raw external corpus is included in the repository.

## 7. Limitations

These datasets are small and synthetic. Their vocabulary and message patterns may not represent real-world spam distribution. Evaluation results therefore indicate performance on the fixed project test set, not guaranteed real-world classification performance.

## 8. Approval Status

Both datasets have been manually reviewed and approved. The project data gate was independently executed and passed on 2026-11-13. The gate validates the documented data requirements and integrity checks; it does not establish real-world representativeness.
