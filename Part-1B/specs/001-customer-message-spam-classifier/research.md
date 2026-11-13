# Research: Customer Message Spam Classifier

**Date**: 2026-11-08

**Scope**: Resolve design choices required by the approved specification and record the constraints that must be checked before dataset creation and use.

## Decisions

### Python interface

- **Decision**: Use a local Streamlit interface for submitting one message and viewing category, confidence, and validation errors.
- **Rationale**: The application is explicitly Python-based and needs a simple local interface. Streamlit avoids introducing a separate frontend language or an independently deployed service. The UI calls the same package API as the evaluator.
- **Alternatives considered**: A separate JavaScript frontend and Python API would add deployment and interface-contract work not required by the single-user scope.

### Classifier pipeline and confidence

- **Decision**: Fit TF-IDF and Multinomial Naive Bayes as one scikit-learn pipeline. Use the maximum of the two predicted class probabilities as confidence and the associated class as the predicted label. Map confidence below 0.70 to REVIEW.
- **Confidence interpretation**: Multinomial Naive Bayes `predict_proba` outputs probability estimates. They are not guaranteed to be calibrated probabilities of correctness. Treat 0.70 as a fixed design threshold, not a promise of 70% empirical accuracy or a target REVIEW rate. Report the observed REVIEW count and rate on the fixed valid evaluation cases.
- **Rationale**: A pipeline ensures the vectorizer is fitted only on training data and that inference repeats the same transformations. The confirmed threshold and score definition map directly to the specification; reporting REVIEW frequency keeps the operational effect of this fixed threshold visible.
- **Alternatives considered**: Separate transformation and classifier objects risk inconsistent fit/transform handling; a hardcoded pattern classifier violates the constitution.
- **References**:
  - [scikit-learn text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)
  - [scikit-learn MultinomialNB](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html)
  - [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

### Dataset source, authorship, and privacy

- **Decision**: Use a self-authored synthetic labeled dataset for both training and held-out evaluation, following the instructor's recommendation. No external corpus, including the UCI SMS Spam Collection, is required.
- **Rationale**: Self-authored synthetic examples avoid external dataset licensing and raw-corpus privacy concerns. This approach also allows the project to document the origin and intended labels of its examples.
- **Training data**: Create original synthetic English-language messages labeled SPAM or HAM. These messages are used for model training and fitting the TF-IDF vectorizer.
- **Held-out evaluation data**: Create a separate set of at least 15 original synthetic English-language SPAM/HAM messages, with at least five examples per class. These cases are reserved for classification-quality evaluation and must not be used for model training, TF-IDF fitting, vocabulary construction, or any other data-fitting step.
- **Scenario coverage**: The held-out evaluation suite must cover normal, boundary, ambiguous, and adversarial scenarios. Additional synthetic controlled cases may be included for scenario and guardrail checks, but must be identified separately and must not be misrepresented as held-out quality cases.
- **Validation-only cases**: Missing, empty, malformed, non-text, and other invalid inputs must be maintained in a separate validation-only group. These cases are used to test safe validation behavior and are excluded from macro-F1.
- **Privacy safeguards**: Use original fictional message content and avoid real names, phone numbers, email addresses, URLs, credentials, or other personal information. Review the authored examples before committing them. Do not include actual customer messages or copied examples from external datasets.
- **Provenance documentation**: Record that the messages are self-authored synthetic examples, document how they were created and labeled, and distinguish training, held-out evaluation, supplemental controlled, and validation-only groups.
- **Limitations**: Synthetic examples cannot establish real-world spam-classification performance or represent the full range of actual customer messages. Any measured quality score must be described as performance on this fixed synthetic evaluation set, not as a guarantee of real-world accuracy.
- **Alternatives considered**: Using UCI SMS Spam Collection would introduce external dataset licensing, attribution, and privacy-review requirements. The instructor recommended self-authored synthetic data as the simpler approach. Therefore, no external corpus is selected for this project.

### Train/evaluation separation and repeatability

- **Decision**: Create separate, self-authored synthetic training and held-out evaluation datasets. Freeze the held-out messages, IDs, labels, scenario types, and requirement references before final evaluation. Fit the complete TF-IDF and Multinomial Naive Bayes pipeline using training data only. Keep every held-out evaluation message and label out of all model and preprocessing fitting.
- **Data separation**: Ensure no held-out evaluation message is copied into the training dataset. Keep supplemental controlled cases and validation-only cases separately identified and outside classification-quality metrics.
- **Repeatability**: Use a fixed random seed wherever data partitioning or randomized processing is used. Preserve the dataset versions and model configuration used for evaluation.
- **Evaluation requirements**: Require at least 15 valid labeled held-out SPAM/HAM cases, with at least five per class. Freeze all cases, IDs, labels, group markers, scenario types, and requirement references. Fail evaluation if required class counts or scenario coverage are missing.
- **Rationale**: Separate datasets prevent evaluation leakage, frozen cases make runs comparable, and fixed acceptance criteria prevent retrospective selection of easier examples.
- **Alternatives considered**: Using the same examples for training and evaluation can produce misleading quality scores. Changing evaluation cases after observing results makes scores incomparable. Fitting TF-IDF before separating the datasets leaks vocabulary information from evaluation data.

### Independent evaluation

- **Decision**: Keep evaluator orchestration separate from the UI and have it invoke the package's public classification function. Validate result and error structures, category/confidence invariants, the REVIEW threshold, invalid-input rejection, and classification metrics independently. Report SPAM and HAM precision, recall, and F1; macro-F1; REVIEW count and rate; and the total valid evaluation case count. Count REVIEW as incorrect for a labeled SPAM/HAM case. Keep structural validation, invariant/property validation, and classification-quality evaluation independently runnable and separately reported.
- **Rationale**: This supports repeatable command-line evaluation and prevents the UI from determining evaluation success. Separate outcomes make it clear whether a failure is a malformed result, a violated guardrail, or insufficient class quality.
- **Alternatives considered**: UI-only checks cannot be run independently and do not provide a reliable evaluation report.

### REVIEW threshold boundary tests

- **Decision**: Add deterministic unit tests of the threshold decision using supplied confidence values, independent of model fitting and dataset selection: 0.699 yields REVIEW; 0.700 yields the predicted class; and 0.701 yields the predicted class.
- **Rationale**: Testing the exact boundary rule without depending on learned probabilities isolates and verifies the strict "below 0.70" behavior reproducibly.
- **Alternatives considered**: Relying on model-generated samples to land on exact values is nondeterministic and does not guarantee coverage of the boundary.

## Remaining prerequisite

T004 remains a data acceptance gate. Before training or final evaluation, create and review the self-authored synthetic training and held-out evaluation datasets. Document their synthetic authorship, creation and labeling method, dataset separation, scenario coverage, and privacy review outcome.

Keep training and held-out evaluation examples separate. Verify that no held-out evaluation message or label is used for training or TF-IDF fitting. Ensure the held-out evaluation set contains at least 15 valid labeled cases, with at least five SPAM and five HAM examples, and that the required scenario coverage is present.

Do not mark the data gate complete until the required datasets and documentation have actually been created and reviewed. If any required condition is not satisfied, keep the gate blocked and record the outstanding issue rather than bypassing it.

The fixed held-out evaluation dataset, its labels, coverage requirements, and acceptance criteria must not be changed merely to improve the evaluation score.
