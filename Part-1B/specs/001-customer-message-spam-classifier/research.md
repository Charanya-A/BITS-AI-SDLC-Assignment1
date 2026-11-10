# Research: Customer Message Spam Classifier

**Date**: 2026-11-08
**Scope**: Resolve design choices required by the approved specification and record
the constraints that must be checked before data acquisition.

## Decisions

### Python interface

- **Decision**: Use a local Streamlit interface for submitting one message and
  viewing category, confidence, and validation errors.
- **Rationale**: The application is explicitly Python-based and needs a simple local
  interface. Streamlit avoids introducing a separate frontend language or an
  independently deployed service. The UI calls the same package API as the evaluator.
- **Alternatives considered**: A separate JavaScript frontend and Python API would
  add deployment and interface-contract work not required by the single-user scope.

### Classifier pipeline and confidence

- **Decision**: Fit TF-IDF and Multinomial Naive Bayes as one scikit-learn pipeline.
  Use the maximum of the two predicted class probabilities as confidence and the
  associated class as the predicted label. Map confidence below 0.70 to REVIEW.
- **Confidence interpretation**: Multinomial Naive Bayes `predict_proba` outputs
  probability estimates. They are not guaranteed to be calibrated probabilities of
  correctness. Treat 0.70 as a fixed design threshold, not a promise of 70% empirical
  accuracy or a target REVIEW rate. Report the observed REVIEW count and rate on the
  fixed valid evaluation cases.
- **Rationale**: A pipeline ensures the vectorizer is fitted only on training data
  and that inference repeats the same transformations. The confirmed threshold and
  score definition map directly to the specification; reporting REVIEW frequency
  keeps the operational effect of this fixed threshold visible.
- **Alternatives considered**: Separate transformation and classifier objects risk
  inconsistent fit/transform handling; a hardcoded pattern classifier violates the
  constitution.
- **References**:
  - [scikit-learn text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)
  - [scikit-learn MultinomialNB](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html)
  - [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

### Dataset provenance, license, and privacy

- **Verification basis**: The license, provenance, checksums, and statistics below
  reflect the completed dataset review supplied for this planning update. No corpus
  was acquired, downloaded, or independently re-verified as part of this document
  change.
- **Primary dataset decision**: Accept UCI SMS Spam Collection v1 as the primary
  corpus, subject to the project data-rights/provenance/privacy acceptance gate.
  The official [UCI record](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
  identifies the dataset as CC BY 4.0 and attributes it to Tiago Almeida and JosÃ©
  Hidalgo. Preserve academic attribution to the original authors and the original
  dataset README's request for attribution and recommendation to contact the authors
  when using the corpus.
- **Verified archive details**: `sms+spam+collection.zip` SHA-256:
  `1587EA43E58E82B14FF1F5425C88E17F8496BFCDB67A583DBFF9EEFAF9963CE3`;
  extracted `SMSSpamCollection` SHA-256:
  `7D039A24A6083ED9EF0F806EBAD56BBB976E3AEB8DE05669173BFDC4996C239D`;
  original README SHA-256:
  `8753CD2D3CAB68F80C8257851B8C2037778C267F55ACCB6FD1B5A2E32D36A84E`.
- **Reviewed data statistics**: 5,574 total records (4,827 HAM and 747 SPAM);
  zero empty and zero malformed records; 5,159 unique normalized messages; 290
  duplicate groups covering 705 records, with 415 extra repeated occurrences;
  zero conflicting-label duplicate groups; 7 email-pattern matches, 422
  phone-like-pattern matches, 108 URL-pattern matches, and zero Unicode replacement
  characters.
- **Required safeguards**: Keep the downloaded original corpus outside the Git
  repository and do not commit raw corpus data. Use only its label and message text.
  Normalize messages consistently and deduplicate by normalized message before
  partitioning. Split unique normalized-message groups into training and held-out
  evaluation partitions, with no normalized message in both partitions and class
  representation preserved. Keep at least 15 valid, labeled SPAM/HAM classification
  cases, with at least five per class, from the held-out UCI partition after
  deduplication and example-level privacy review. Exclude or appropriately handle
  examples with potential personal information; never expose raw phone numbers,
  email addresses, or other sensitive content in committed fixtures, logs, or
  evidence. Other scenarios need not be sourced from UCI: separately identify
  supplemental synthetic or controlled cases for ambiguous, adversarial, or
  boundary behavior where appropriate. Clearly mark those cases as synthetic or
  controlled and never represent them as UCI records. Use them for scenario and
  guardrail checks, not the held-out UCI macro-F1 calculation. Keep missing and
  malformed inputs in a separate validation-only group; check them for safe
  validation errors and exclude them from macro-F1.
- **Privacy-screening limitation**: Email, phone-like, and URL pattern counts are
  screening indicators only; they do not confirm personal information or prove
  anonymization. Document residual privacy risks and the limitations of automated
  screening. Review evaluation examples before committing them; do not treat an
  automated no-match result as proof that an example is safe.
- **Reviewed, not selected**: The Mendeley SMS Phishing Dataset was examined but
  rejected as the primary corpus because it requires more complicated label mapping
  (`HAM`, `SPAM`, `SMISHING`) and contains additional `URL`, `EMAIL`, and `PHONE`
  columns. This selection decision is not a finding that its licensing is invalid.
- **Alternatives considered**: The Mendeley corpus is not selected for this scope.
  Synthetic or controlled cases may supplement scenario/guardrail coverage but do
  not replace or count toward the minimum held-out UCI classification cases.

### Train/evaluation separation and repeatability

- **Decision**: Record corpus version, provenance, license, source/archive and
  extracted-file checksums, and split seed. Normalize consistently and deduplicate
  before partitioning; split unique normalized-message groups deterministically
  into training and held-out evaluation partitions while preserving class
  representation. Keep every held-out evaluation message out of model and
  preprocessing fitting, including TF-IDF. Require at least 15 privacy-reviewed
  held-out UCI valid labeled classification cases, including at least five per
  class. Supplemental synthetic/controlled scenario cases must be identified as
  such, never labeled as UCI, and may provide scenario/guardrail coverage where
  appropriate; do not include these supplemental cases in the held-out UCI
  macro-F1 calculation. Keep missing/malformed validation-only cases separately
  identified and outside classification metrics. Freeze all cases, IDs, labels,
  source/type markers, scenario types, and requirement references; fail evaluation
  if required class counts or scenario coverage are missing.
- **Rationale**: Group-level splitting prevents duplicate leakage, deterministic
  partitioning makes runs comparable, preserving class representation retains both
  classes, and a frozen holdout prevents retrospective selection.
- **Alternatives considered**: Splitting records before deduplication can put the
  same normalized message on both sides; a new random test sample for every run
  makes scores incomparable; fitting TF-IDF before partitioning leaks vocabulary
  information from evaluation data.

### Independent evaluation

- **Decision**: Keep evaluator orchestration separate from the UI and have it invoke
  the package's public classification function. Validate result and error structures,
  category/confidence invariants, the REVIEW threshold, invalid-input rejection, and
  classification metrics independently. Report SPAM and HAM precision, recall, and
  F1; macro-F1; REVIEW count and rate; and the total valid evaluation case count.
  Count REVIEW as incorrect for a labeled SPAM/HAM case. Keep structural validation,
  invariant/property validation, and classification-quality evaluation independently
  runnable and separately reported.
- **Rationale**: This supports repeatable command-line evaluation and prevents the
  UI from determining evaluation success. Separate outcomes make it clear whether a
  failure is a malformed result, a violated guardrail, or insufficient class quality.
- **Alternatives considered**: UI-only checks cannot be run independently and do not
  provide a reliable evaluation report.

### REVIEW threshold boundary tests

- **Decision**: Add deterministic unit tests of the threshold decision using supplied
  confidence values, independent of model fitting and corpus selection: 0.699 yields
  REVIEW; 0.700 yields the predicted class; and 0.701 yields the predicted class.
- **Rationale**: Testing the exact boundary rule without depending on learned
  probabilities isolates and verifies the strict "below 0.70" behavior reproducibly.
- **Alternatives considered**: Relying on model-generated samples to land on exact
  values is nondeterministic and does not guarantee coverage of the boundary.

## Remaining prerequisite

The primary UCI dataset has been selected based on the stated provenance and
license review. T004 remains a hard acceptance gate to record the source and license,
preserve attribution and README terms, verify the recorded archive/file checksums,
and approve the processing and evaluation-example privacy safeguards before project
acquisition/use, training, or committing any evaluation examples. Keep the original
download outside Git. If the required provenance or privacy checks cannot be
completed, block affected data-dependent work and request direction; do not bypass
the gate.

The fixed, privacy-reviewed evaluation dataset must remain separate from training,
including TF-IDF fitting. Its labels, cases, coverage requirements, and acceptance
criteria must not be changed merely to improve the score.
