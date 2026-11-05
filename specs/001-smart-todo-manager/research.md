# Research: Smart Todo & Task Manager

## Decision 1: Split the application into a Vite React frontend and an Express backend

- Decision: Build the product as a web application with a React + Vite frontend and a separate Node.js + Express backend exposing REST endpoints.
- Rationale: The approved constitution requires a React + Vite frontend, Node.js + Express backend, and REST APIs. Separating the UI and API keeps validation, JSON persistence, and task logic under backend control while keeping the frontend presentation layer simple and deterministic.
- Alternatives considered: A single monolithic frontend-only app or a direct file access layer from the browser. Both conflict with the assignment requirements and the approved backend validation and persistence rules.

## Decision 2: Use a single JSON file for local persistence only

- Decision: Store the task collection in one local JSON file, with the backend acting as the only writer and the frontend reading data through REST endpoints.
- Rationale: The specification explicitly requires JSON file-based persistence, no external database, and safe startup recovery for malformed storage. A single file keeps the system deterministic and easy to validate.
- Alternatives considered: SQLite, MongoDB, or a second service state store. These are explicitly disallowed by the constitution and would violate the approved scope.

## Decision 3: Enforce a strict task domain model and validation layer

- Decision: Use server-side validation for all incoming requests before persistence, with a canonical `Task` schema and an explicit status model.
- Rationale: The specification requires a stable unique ID, trimmed title validation, description limits, tag sanitization, deterministic priority values, and explicit status transition rules.
- Alternatives considered: Allowing loose client-side validation or partial server-side checks. Rejected because invalid inputs and malformed storage must not corrupt persisted data.

## Decision 4: Treat status transitions as a dedicated state machine

- Decision: Allow only `PENDING -> IN_PROGRESS` and `IN_PROGRESS -> COMPLETED`, and reject all other transitions including repeated current-state requests.
- Rationale: The assignment explicitly requires strict status transition rules and error handling. The dedicated `/api/tasks/:id/status` endpoint prevents the general update endpoint from mutating status values.
- Alternatives considered: Allowing free-form status updates or using general PATCH to mutate status. Rejected because it would conflict with the approved contract and data integrity requirements.

## Decision 5: Use atomic writes and explicit error responses

- Decision: Serialize writes in the single application process, write to a temporary file, and atomically replace the main storage file. Runtime read/write errors return a sanitized persistence error structure.
- Rationale: The specification demands that malformed storage at startup does not silently reset the file, failed writes do not leave partial JSON, and clients receive safe error messages without filesystem details or stack traces.
- Alternatives considered: In-place writes or direct `fs.writeFileSync` without a temp-file guard. Rejected because they risk data corruption and violate the persistence safeguards.

## Decision 6: Use deterministic sorting without mutating stored order

- Decision: Sort only in the response layer using `HIGH`, `MEDIUM`, `LOW`, then `createdAt`, then `id` for ties, while leaving the underlying JSON file unchanged.
- Rationale: The assignment requires deterministic order and explicitly states that sorting must not modify persisted data.
- Alternatives considered: Sorting in-place on the JSON store. Rejected because it would violate the specification and increase persistence risk.

## Decision 7: Use automated verification as part of the delivery gate

- Decision: Plan for unit tests, API/contract tests, lint/syntax checks, and harness evidence capture for initial and final generation.
- Rationale: The constitution requires evidence-driven delivery, verification, and final acceptance by a human after all required automated checks pass.
- Alternatives considered: Manual-only validation or skipping negative-case tests. Rejected because this would violate the assignment requirements and quality gates.

## Decision 8: Target Node.js 24 LTS and standardize the API contract

- Decision: Target Node.js 24 LTS for the backend runtime and capture the task API contract in OpenAPI with explicit validation, status, and persistence behavior.
- Rationale: The planning artifacts must match the approved environment target and the finalized API semantics exactly, including validation error distinctions, 404/409 handling, and safe persistence failures.
- Alternatives considered: Omitting an explicit runtime target or relying on informal documentation alone. Rejected because this would reduce reproducibility and could drift from the approved requirements.

## Open Issues

- No genuine specification conflicts remain after the approved clarifications.
- The only intentional scope boundary is that cross-process coordination is out of scope; the solution only needs safe single-process serialization for local JSON writes.
- OpenAPI can express most request constraints, but server-side validation of trimmed values, empty PATCH bodies, and runtime persisted-state invariants must remain documented in prose and enforced in code.
