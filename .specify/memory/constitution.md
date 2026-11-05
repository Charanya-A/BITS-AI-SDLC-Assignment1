# AI-SDLC Assignment 1 Part-1A Constitution

<!-- Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles: none; existing five principles preserved
- Added sections: assignment-specific engineering constraints and validation requirements
- Removed sections: none
- Deferred items: none
-->

## Core Principles

### I. Evidence-Driven Delivery
All work in this repository must be grounded in clear requirements, reproducible evidence, and explicit validation. Features, fixes, and documentation changes require a traceable link to a problem statement, user need, or assignment objective; no undocumented assumptions or "it seems right" changes.

Rationale: this project is instructional and evaluative, so evidence is the basis for correctness and fair review.

### II. Quality Before Speed
Quality gates are non-negotiable: correctness, readability, maintainability, and testability must be satisfied before completion is claimed. Shortcuts, dead code, or unverified outputs are not allowed.

Rationale: assignment work must remain reviewable, reproducible, and safe to build upon.

### III. Test-First and Verification
Any behavior-changing change must have a clear verification path before completion, usually through automated tests, targeted checks, or documented validation. The work may not be considered done until the relevant checks pass.

Rationale: software quality depends on evidence, not intent.

### IV. Modularity and Maintainability
Each feature, script, or module must have a single clear purpose, be understandable in isolation, and avoid unnecessary coupling. Shared logic must be named and reused deliberately rather than duplicated.

Rationale: explicit boundaries reduce confusion and make the repository easier to extend or assess.

### V. Clear Communication and Review
Changes must be easy to inspect, explain, and review. Commit messages, comments, naming, and documentation must be specific enough that another engineer can understand the intent without hidden context.

Rationale: transparent work supports fair evaluation, easier debugging, and sustainable maintenance.

## Additional Constraints
This repository is used for the Smart Todo & Task Manager assignment and must follow the approved engineering stack and constraints for that assignment. The approved stack is React with Vite for the frontend, Node.js with Express.js for the backend, a REST API architecture, and JSON file-based persistence. MongoDB or any other database technology must not be introduced for this task.

Functionality must satisfy the assignment requirements exactly. The backend and frontend must support task creation, retrieval, updating, and deletion; task tags and tag-based filtering; deterministic priority sorting using explicitly defined priority levels; explicit task-status values with allowed transitions; and rejection of invalid status transitions without changing persisted data. Every task must have a unique, stable ID. The backend must validate all incoming data, reject malformed input before it is persisted, and ensure that malformed data never corrupts existing JSON records. Failed persistence operations must return a clear error message, and individual task operations must not modify unrelated tasks.

Testing and traceability are mandatory. Every approved functional requirement must map to one or more acceptance criteria and automated tests, including positive, negative, and boundary cases. API responses must include appropriate HTTP status codes for success and failure conditions, and all required automated tests must pass before final acceptance. Quality requirements are measurable: acceptance criteria must be explicit in the specification rather than subjective, required tests must pass, and no unresolved critical security findings may remain at final acceptance.

Security constraints are mandatory and non-negotiable. No API keys, passwords, credentials, secrets, or other sensitive values may be committed to the repository. All input must be validated and sanitized before processing, and internal errors or sensitive filesystem details must not be exposed to clients. The project must not rely on hidden assumptions or down-level security exceptions to pass validation.

Harness integrity must be preserved. The original generated implementation must be preserved before any harness-driven corrections are made. The required validation gates include syntax and lint checks, security analysis, unit tests, and API or contract tests. Actual command outputs, failed checks, and expected-versus-observed results must be recorded. The coding agent must never delete failing tests, weaken assertions, modify approved acceptance criteria, bypass gates, or disable security checks merely to obtain a passing result. Repairs must address the genuine failure evidence, and the same validation gates must be rerun after repairs. Final acceptance or rejection must be made by a human, and no validation evidence may be fabricated.

## Development Workflow
Every task must begin with a clear scope, expected outcome, and validation method. Small, reviewable increments are preferred over large, opaque changes. Work must be traceable to assignment requirements, and any blocker caused by missing requirements or uncertain assumptions must be documented before continuing.

All required checks must be executed as part of completion. The workflow must include syntax and lint validation, security analysis, unit testing, and API or contract testing. For each approved functional requirement, the implementation must be linked to the relevant acceptance criteria and automated tests covering positive, negative, and boundary cases. All required tests must pass before the work is considered complete, and failures must be investigated using the actual evidence rather than bypassed with weakened assertions or altered acceptance criteria.

Final completion requires a verification step and a concise summary of what changed and how it was checked. Rework is expected when validation exposes defects, but those defects must be resolved and the same validation gates rerun before final acceptance. The final state of the project must preserve the original generated implementation before harness correction and must not leave unresolved critical security findings.

## Governance
This constitution supersedes informal local practices for this repository. Amendments require a written rationale, review of the affected principle or section, and an incremented version number. Any material change must be documented in this file before it is considered authoritative.

Versioning policy follows semantic versioning: MAJOR for backward-incompatible governance or principle changes, MINOR for added or materially expanded guidance, and PATCH for clarifications or non-semantic refinements. A change to the constitution is not complete until the version and amendment date are recorded.

Compliance review expectations are mandatory. Every change must be checked against the relevant principles, and the validation evidence that supports completion must be retained with the work. Contributors are expected to confirm that quality gates were met before claiming the task is done. In this assignment, final ACCEPT or REJECT decisions must remain human-controlled, based on actual validation evidence, and free from fabricated or suppressed failures.

**Version**: 1.1.0 | **Ratified**: 2026-11-05 | **Last Amended**: 2026-11-05
