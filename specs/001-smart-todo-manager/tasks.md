# Tasks: Smart Todo & Task Manager

**Input**: Design documents from `/specs/001-smart-todo-manager/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Automated tests are required for the assignment and are explicitly included in the task list below, including unit, persistence, API/contract, and frontend component coverage.

**Organization**: Tasks are grouped by user story and by shared foundation work to enable independent implementation, verification, and review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete shared task)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the project skeleton, runtime target, and validation tooling before feature work.

- [ ] T001 Create the repository structure for the approved React + Vite frontend and Node.js + Express backend in `backend/src/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`, and `evidence/`
- [ ] T002 Initialize the Node.js 24 LTS backend runtime in `backend/package.json` with the required Express.js runtime, JSON file persistence support, and test tooling for unit/API validation
- [ ] T003 [P] Initialize the React + Vite frontend in `frontend/package.json`, `frontend/index.html`, and `frontend/vite.config.js` to match the approved plan and technology stack
- [ ] T004 [P] Configure shared lint and test scripts in `backend/package.json` and `frontend/package.json` for syntax checks, unit tests, API tests, and frontend component tests
- [ ] T005 Create the evidence directory structure for `evidence/initial-generation/`, `evidence/final-generation/`, and `harness-log.md` inside the approved project structure after T001 so validation output can be preserved and reviewed; this task depends on T001 and must be completed before any harness evidence or repair sequence begins

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the backend architecture, validation layer, storage semantics, deterministic sorting, and test-first foundation required by all stories.

**Critical gate**: No user story work may begin until this phase is complete.

- [ ] T006 Create the backend bootstrap in `backend/src/server.js` and `backend/src/app.js` so the API listens on the approved local port and loads the task store safely
- [ ] T007 Implement shared validation rules and error helpers in `backend/src/services/validationService.js` and `backend/src/utils/errors.js` for `VALIDATION_ERROR`, `MALFORMED_REQUEST`, `NOT_FOUND`, `INVALID_STATUS_TRANSITION`, and `PERSISTENCE_ERROR`; centralize input validation in `validationService.js` and keep `taskService.js` focused on task operations and business logic
- [ ] T008 Implement the task persistence layer in `backend/src/services/storageService.js` to initialize missing or empty JSON files, preserve malformed existing JSON at startup, and perform atomic temp-file writes with single-process serialization before any write is committed
- [ ] T009 Create the canonical task model and enums in `backend/src/models/taskModel.js` for `id`, `title`, `description`, `priority`, `tags`, `status`, `createdAt`, and `updatedAt` and enforce the approved server-generated UUID v4 and UTC ISO 8601 timestamp rules; keep validation and tag trimming/non-empty checks centralized in `validationService.js`
- [ ] T010 Implement deterministic sorting logic in `backend/src/utils/sort.js` for `HIGH`, `MEDIUM`, `LOW` ordering and tie-breaking by `createdAt`, then by `id` lexicographic order; do not mutate persisted records
- [ ] T011 Establish the API route skeleton in `backend/src/routes/tasks.js` for `POST /api/tasks`, `GET /api/tasks`, `GET /api/tasks/:id`, `PATCH /api/tasks/:id`, `PATCH /api/tasks/:id/status`, and `DELETE /api/tasks/:id` as defined in the approved contract
- [ ] T012 [P] Create the frontend API client in `frontend/src/services/api.js` to call the backend REST endpoints and normalize the approved response envelope `{ "data": ... }` and error envelope `{ "error": { ... } }`
- [ ] T013 [P] Add failing unit tests in `backend/tests/unit/taskModel.test.js` for server-generated UUID v4 IDs, UTC ISO 8601 timestamps, required fields, enum validation, and the invariant that clients cannot provide or overwrite `id`, `createdAt`, or `updatedAt`; run the relevant backend test script to confirm the failure baseline before implementing the model
- [ ] T014 [P] Add failing unit tests in `backend/tests/unit/validationService.test.js` for trimmed title validation, empty and oversized description handling, valid and invalid tags, default status behavior, empty PATCH-body rejection, unsupported-field rejection, and `status` restrictions on `PATCH /api/tasks/:id`; run the relevant backend validation tests first so the failing baseline is recorded before implementation
- [ ] T015 [P] Add failing unit tests in `backend/tests/unit/storageService.test.js` for missing JSON store initialization, empty JSON store initialization, malformed existing JSON causing startup failure without overwriting the original file, unreadable existing store behavior, safe runtime persistence failures, failed writes not leaving partial JSON, and serialized writes preserving unrelated tasks; execute the storage tests before implementation to establish the failing baseline
- [ ] T016 [P] Add failing unit tests in `backend/tests/unit/sort.test.js` for priority ordering, tie-break rules, and non-mutating sort behavior; run the sorting unit tests before the implementation that satisfies them

**Checkpoint**: Foundation ready - user story implementation can now begin against the shared validation and persistence contracts.

---

## Phase 3: User Story 1 - Create a task reliably (Priority: P1) 🎯 MVP

**Goal**: Allow valid task creation with backend validation and safe rejection of malformed payloads.

**Independent Test**: A valid task creation request creates a stored task; an invalid request does not alter the store.

### Tests for User Story 1

- [ ] T017 [P] [US1] Add failing API tests in `backend/tests/api/tasks-create.api.test.js` for successful creation `201`, invalid create payloads `400`, and no-write behavior when validation fails
- [ ] T018 [P] [US1] Add frontend component tests in `frontend/tests/unit/TaskForm.test.jsx` for valid create inputs, invalid inputs, tag parsing, default status behavior, and invalid submission without mutating the task list

### Implementation for User Story 1

- [ ] T019 [US1] Implement create-task validation in `backend/src/services/validationService.js` and task-creation orchestration in `backend/src/services/taskService.js` so `title` is required, trimmed to 1-120 chars; `description` is required as a field and may be empty up to 2000 chars; `priority` is `LOW`, `MEDIUM`, or `HIGH`; `tags` defaults to `[]` and each tag is trimmed and non-empty; `status` defaults to `PENDING`; and server-generated `id`, `createdAt`, and `updatedAt` are enforced with centralized validation in `validationService.js` and business logic in `taskService.js`
- [ ] T020 [US1] Add the controller logic for `POST /api/tasks` in `backend/src/controllers/taskController.js` and return `201` with `{ "data": task }` on success, with the approved error envelope on invalid input or persistence failure
- [ ] T021 [US1] Add the `POST /api/tasks` route in `backend/src/routes/tasks.js` and reject malformed or unsupported payloads before any persistence change
- [ ] T022 [US1] Implement the create form and submission flow in `frontend/src/components/TaskForm.jsx` and the task creation handler in `frontend/src/pages/TaskDashboard.jsx` so a user can enter title, description, priority, tags, and optional status; the UI must call the backend API and surface validation messages without mutating local state on failed submit
- [ ] T023 [US1] Add frontend task creation wiring in `frontend/src/App.jsx` and `frontend/src/services/api.js` to render and submit the task form against the approved REST contract

**Checkpoint**: User Story 1 should be functional and independently testable.

---

## Phase 4: User Story 2 - View all tasks and individual tasks (Priority: P1)

**Goal**: Retrieve the task collection and fetch a single task by ID with safe not-found handling.

**Independent Test**: The API returns all persisted tasks and a specific task by ID; unknown IDs return a consistent `404` error.

### Tests for User Story 2

- [ ] T024 [P] [US2] Add failing API tests in `backend/tests/api/tasks-read.api.test.js` for `GET /api/tasks`, `GET /api/tasks/:id`, `tag` filtering, and `404` handling for missing tasks
- [ ] T025 [P] [US2] Add frontend component tests in `frontend/tests/unit/TaskList.test.jsx` for rendering the task collection, empty-state handling, and per-task details display

### Implementation for User Story 2

- [ ] T026 [US2] Implement list and lookup logic in `backend/src/services/taskService.js` to return all tasks and an individual task by stable ID without mutating persistent data
- [ ] T027 [US2] Add GET handlers in `backend/src/controllers/taskController.js` for collection and single-item retrieval, returning the approved response envelopes and status codes
- [ ] T028 [US2] Complete the GET routes in `backend/src/routes/tasks.js` for `GET /api/tasks` and `GET /api/tasks/:id` with the optional `tag` and `sort=priority` support required by the contract
- [ ] T029 [US2] Implement the task list and detail UI in `frontend/src/components/TaskList.jsx` and `frontend/src/components/TaskCard.jsx` so tasks are displayed with title, description, priority, tags, status, and timestamps, and task-detail retrieval is shown without exposing internal errors
- [ ] T030 [US2] Wire the dashboard page in `frontend/src/pages/TaskDashboard.jsx` to load the full task list on startup and refresh after create/update/delete actions

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Update permitted task fields without altering unrelated tasks (Priority: P1)

**Goal**: Allow safe partial updates to the approved task fields while rejecting unsupported modifications and preserving task identity.

**Independent Test**: Only permitted fields change; the task ID and status remain immutable through the general PATCH route.

### Tests for User Story 3

- [ ] T031 [P] [US3] Add failing API tests in `backend/tests/api/tasks-update.api.test.js` for valid partial updates, invalid payloads, empty PATCH bodies, unsupported fields, and rejected status updates through `PATCH /api/tasks/:id`
- [ ] T032 [P] [US3] Add frontend component tests in `frontend/tests/unit/TaskEditor.test.jsx` for editing title, description, priority, and tags while rejecting status updates from the generic editor and preserving other tasks

### Implementation for User Story 3

- [ ] T033 [US3] Implement general task update validation in `backend/src/services/validationService.js` to allow only `title`, `description`, `priority`, and `tags`, reject empty payloads and unknown fields, and reject `status` and server-managed fields through this endpoint; the service must remain the single validation authority and `taskService.js` must not duplicate these rules
- [ ] T034 [US3] Implement partial update logic in `backend/src/services/taskService.js` so fields are applied only when provided, `updatedAt` changes on success, and unrelated tasks remain untouched
- [ ] T035 [US3] Add the PATCH route and controller logic in `backend/src/routes/tasks.js` and `backend/src/controllers/taskController.js` for `PATCH /api/tasks/:id` with `200` success and `400` / `404` error handling
- [ ] T036 [US3] Implement the edit modal or inline editor in `frontend/src/components/TaskEditor.jsx` to update permitted fields only, preserve the task ID, and reject unsupported status edits through the generic update UI
- [ ] T037 [US3] Ensure the dashboard in `frontend/src/pages/TaskDashboard.jsx` refreshes only the edited task and leaves unrelated task rows unchanged when updates succeed or fail

**Checkpoint**: User Story 3 should be independently testable and data-safe.

---

## Phase 6: User Story 4 - Delete a task safely (Priority: P1)

**Goal**: Delete a selected task while keeping unrelated tasks and not-found semantics correct.

**Independent Test**: An existing task is deleted; a missing task returns `404`; other tasks remain unchanged.

### Tests for User Story 4

- [ ] T038 [P] [US4] Add failing API tests in `backend/tests/api/tasks-delete.api.test.js` for successful delete `204`, missing ID `404`, and no unintended modifications to other tasks
- [ ] T039 [P] [US4] Add frontend component tests in `frontend/tests/unit/TaskActions.test.jsx` for delete confirmation, cancel behavior, and ensuring unrelated tasks remain visible after a failed or successful delete

### Implementation for User Story 4

- [ ] T040 [US4] Implement delete logic in `backend/src/services/taskService.js` to remove only the matched task, return a clear not-found error for unknown IDs, and preserve unaffected tasks
- [ ] T041 [US4] Add the `DELETE /api/tasks/:id` route and controller handler in `backend/src/routes/tasks.js` and `backend/src/controllers/taskController.js` with `204` success and `404` error handling
- [ ] T042 [US4] Add a task delete confirmation flow in `frontend/src/components/TaskActions.jsx` and `frontend/src/pages/TaskDashboard.jsx` so deletion is confirmed before removing a task and the UI handles `404` and API errors gracefully
- [ ] T043 [US4] Validate that delete operations use the safe atomic write path and do not leave partial JSON data in `backend/src/services/storageService.js`

**Checkpoint**: User Story 4 is independently functional and safe.

---

## Phase 7: User Story 5 - Manage tags and filter by tag (Priority: P1)

**Goal**: Support multiple tags, case-insensitive filtering, and exclusion of non-matching tasks.

**Independent Test**: Filtering by tag returns matching tasks and omits non-matches in a case-insensitive manner.

### Tests for User Story 5

- [ ] T044 [P] [US5] Add failing API tests in `backend/tests/api/tasks-tags.api.test.js` for tag queries, mixed-case matching, empty results, and non-matching exclusions
- [ ] T045 [P] [US5] Add frontend component tests in `frontend/tests/unit/TaskFilter.test.jsx` for tag filter controls, case-insensitive input handling, and empty filtered states

### Implementation for User Story 5

- [ ] T046 [US5] Implement tag normalization and tag-based filtering in `backend/src/services/taskService.js` so matches are case-insensitive and tasks without matching tags are excluded
- [ ] T047 [US5] Update the `GET /api/tasks` route and controller in `backend/src/routes/tasks.js` and `backend/src/controllers/taskController.js` to accept the optional `tag` query parameter without changing stored order
- [ ] T048 [US5] Define the canonical task schema in `backend/src/models/taskModel.js` for the task structure, fields, enums, and defaults; keep incoming tag validation, trimming, non-empty checks, and rejection before persistence centralized in `backend/src/services/validationService.js`; do not duplicate input-validation rules in `taskModel.js` or `taskService.js`
- [ ] T049 [US5] Add tag display and filtering controls in `frontend/src/components/TaskFilter.jsx` and `frontend/src/pages/TaskDashboard.jsx` so users can select or enter a tag, filter the table/list, and see matching tasks only
- [ ] T050 [US5] Add tag editing support in `frontend/src/components/TaskEditor.jsx` and `frontend/src/components/TaskForm.jsx` for multiple tags with trimming and validation consistent with the backend rules

**Checkpoint**: Tag management and filtering are independently verified.

---

## Phase 8: User Story 6 - Sort tasks by priority deterministically (Priority: P1)

**Goal**: Return tasks in the approved deterministic priority order and keep the persisted storage order unchanged.

**Independent Test**: Priority sorting follows `HIGH`, `MEDIUM`, `LOW`, with tie-breaking by `createdAt` then `id`; sorting does not rewrite the JSON file.

### Tests for User Story 6

- [ ] T051 [P] [US6] Add failing unit tests in `backend/tests/unit/sort.test.js` for ordering rules and tie-break logic
- [ ] T052 [P] [US6] Add failing API tests in `backend/tests/api/tasks-sort.api.test.js` for `?sort=priority` and persistence invariants
- [ ] T053 [P] [US6] Add frontend component tests in `frontend/tests/unit/TaskSort.test.jsx` for priority sorting control visibility and correct render order of tasks by priority

### Implementation for User Story 6

- [ ] T054 [US6] Implement the deterministic priority sorting algorithm in `backend/src/utils/sort.js` and ensure it does not mutate stored records or persisted order
- [ ] T055 [US6] Wire `sort=priority` handling into `GET /api/tasks` in `backend/src/routes/tasks.js` and `backend/src/controllers/taskController.js`
- [ ] T056 [US6] Implement sorting controls in `frontend/src/components/TaskToolbar.jsx` and `frontend/src/pages/TaskDashboard.jsx` to support priority sorting and display the approved `HIGH`, `MEDIUM`, `LOW` order without altering the persisted backing store
- [ ] T057 [US6] Verify that all equal-priority tasks are ordered by `createdAt` ascending then `id` lexicographically and that the sorting logic matches the approved contract in `specs/001-smart-todo-manager/contracts/task-api.yaml`

**Checkpoint**: Priority ordering is deterministic and non-mutating.

---

## Phase 9: User Story 7 - Manage task status with valid transitions (Priority: P1)

**Goal**: Enforce the approved status state machine and dedicated status endpoint without allowing unsafe transitions.

**Independent Test**: Allowed transitions succeed; disallowed or repeated transitions return `409` and leave the stored task unchanged.

### Tests for User Story 7

- [ ] T058 [P] [US7] Add failing API tests in `backend/tests/api/tasks-status.api.test.js` for `PENDING -> IN_PROGRESS`, `IN_PROGRESS -> COMPLETED`, rejected transitions, repeated same-state transitions, and `409` response codes
- [ ] T059 [P] [US7] Add unit tests in `backend/tests/unit/validationService.test.js` for invalid status values, unsupported transitions, and the requirement that `PATCH /api/tasks/:id` rejects `status`
- [ ] T060 [P] [US7] Add frontend component tests in `frontend/tests/unit/TaskStatus.test.jsx` for displaying status badges, updating status via the dedicated endpoint, and rejecting invalid transitions with user-visible error feedback

### Implementation for User Story 7

- [ ] T061 [US7] Implement the status transition gate in `backend/src/services/validationService.js` to determine whether a requested status change is allowed; `backend/src/services/taskService.js` orchestrates the status update and persistence, with no duplicate state-machine validation in both files
- [ ] T062 [US7] Add the dedicated status endpoint in `backend/src/routes/tasks.js` and `backend/src/controllers/taskController.js` for `PATCH /api/tasks/:id/status` with `200` on success and `400` / `404` / `409` on invalid inputs or invalid transitions
- [ ] T063 [US7] Implement status controls in `frontend/src/components/TaskStatus.jsx` and `frontend/src/pages/TaskDashboard.jsx` to display `PENDING`, `IN_PROGRESS`, and `COMPLETED`, update the task status using the dedicated backend endpoint, and prevent invalid transitions from mutating the UI state
- [ ] T064 [US7] Ensure the general `PATCH /api/tasks/:id` path rejects any status field, and validate that the `INVALID_STATUS_TRANSITION` response schema is used exactly as defined in `specs/001-smart-todo-manager/spec.md` and `task-api.yaml` with no data mutation on rejected transitions

**Checkpoint**: Status management is validated and consistent with the approved contract.

---

## Phase 10: Validation, Security, and Harness Evidence

**Purpose**: Preserve evidence for the initial generation, run the required gates, repair genuine failures, rerun the same gates, and leave a human-reviewed final record.

- [ ] T065 Capture the untouched initial-generation snapshot in `evidence/initial-generation/` before any harness-driven corrections, preserving the original generated state for later comparison and ensuring it is not overwritten by any later repair snapshot
- [ ] T066 Run the syntax and lint gate for the frontend and backend using the project scripts in each package (`npm run lint` or the configured equivalent) and record the raw command output, exit status, and observed issues in `harness-log.md`
- [ ] T067 Run the unit-test gate using the configured backend and frontend test scripts, capture the exact command output, failures, expected observations, and actual observations in `harness-log.md`, and do not report the gate as passed before the command runs successfully
- [ ] T068 Run the API and contract-test gate against the backend API tests and `specs/001-smart-todo-manager/contracts/task-api.yaml`, store the exact command output and any mismatches in `harness-log.md`, and compare the results against the approved response and error contracts
- [ ] T069 Run the dependency-vulnerability audit gate using `npm audit --audit-level=high` in the backend and frontend package directories, record the exact output and any findings in `harness-log.md`, and do not claim the audit passed without actual successful command execution
- [ ] T070 Run the required SAST/static-analysis gate using a genuine executable security tool, with a prerequisite such as `npm install -g semgrep` or `python -m pip install semgrep`, followed by `semgrep scan --config p/javascript --error backend/src frontend/src`, and record the exact output and findings in `harness-log.md`; do not treat ESLint or `npm audit` alone as proof that SAST passed
- [ ] T071 Feed the actual failure evidence observed in T066-T070 to the coding agent for repair, preserving the genuine command output, expected results, actual results, and any stack output without inventing or forcing a failure; record honestly whether a gate passed or failed and do not fabricate a repair cycle; the coding agent must repair real failures shown by the validation evidence, not a synthetic or forced failure
- [ ] T072 Capture the corrected final implementation snapshot in `evidence/final-generation/` after repairs, preserving the final state separately from the initial-generation evidence and keeping the initial snapshot intact
- [ ] T073 Rerun the same syntax/lint, unit, API/contract, dependency-audit, and SAST gates after repair using the same criteria and record the exact post-repair outputs in `harness-log.md`
- [ ] T074 Record the final ACCEPT or REJECT decision in `harness-log.md` after human review, ensuring tests, acceptance criteria, and validation gates remain unchanged and no checks are weakened, removed, or disabled to obtain a pass
- [ ] T075 Verify that `harness-log.md` records actual command outputs, failure evidence, expected-versus-observed results, and the final human review outcome without fabricating validation evidence

---

## Phase 11: Cross-Cutting Polish and Traceability

**Purpose**: Confirm the task set covers every approved requirement and leaves no requirement unassigned.

- [ ] T076 Ensure every approved functional requirement, acceptance criterion, API endpoint, error response, persistence safeguard, and success criterion in `specs/001-smart-todo-manager/spec.md` and `specs/001-smart-todo-manager/contracts/task-api.yaml` is mapped to at least one implementation or verification task in this file
- [ ] T077 Ensure the backend validation responsibilities remain centralized in `backend/src/services/validationService.js`, while `backend/src/services/taskService.js` owns task-operation logic and orchestration; do not duplicate validation rules across both service files
- [ ] T078 Ensure the frontend matches the approved React + Vite specification and the plan by covering a complete task-management interface: view, create, edit, delete, filter by tag, priority sort, and status display/update
- [ ] T079 Ensure all persistence, validation, and security tasks explicitly cover the required negative, boundary, and malformed-data scenarios without inventing new behavior beyond the approved specification
- [ ] T080 Record the unresolved ambiguity note: malformed ID handling remains governed by the approved validation and not-found semantics in the specification; no additional custom malformed-ID behavior is introduced beyond the approved requirements
- [ ] T081 Run the final task-file consistency review to confirm the checklist format is still valid, task IDs remain unique and sequential, `[P]` labels are only used where dependencies are truly absent, and all story tasks keep the correct `[USx]` labels

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Stories (Phase 3-9)**: Each depends on the shared foundation and may be implemented in priority order once the foundation passes.
- **Validation and Harness (Phase 10)**: Depends on completed implementation and the initial-generation snapshot.
- **Polish and Traceability (Phase 11)**: Depends on the completed implementation, validation evidence, and human review outputs.

### User Story Dependencies

- **User Story 1 (US1)**: Can start after the foundation, with no dependency on other stories.
- **User Story 2 (US2)**: Depends on the foundation and the create/get task model from US1.
- **User Story 3 (US3)**: Depends on validation, persistence, and the task model from earlier tasks.
- **User Story 4 (US4)**: Depends on the shared task service and storage layer.
- **User Story 5 (US5)**: Depends on the task model, task list retrieval, and validation rules.
- **User Story 6 (US6)**: Depends on the shared list/retrieval layer and sorting helpers.
- **User Story 7 (US7)**: Depends on validation, task model, and status management services.

### Parallel Opportunities

- Setup tasks T003 and T004 are parallelizable; T005 depends on T001 and therefore is not parallel with T003-T004.
- Foundation tasks T008, T011, T012, T013, T014, T015, and T016 are parallelizable only when their dependencies are already satisfied and shared files are not being edited concurrently.
- Tests for each user story are parallelizable with one another when they target separate files and shared infrastructure is complete.
- Frontend UI tasks for a story can run in parallel when they target different files and do not depend on unfinished shared components.
- Validation and harness tasks T065-T075 are sequential evidence and review activities and must follow the defined order; they are not parallelizable.

---

## Parallel Example: User Story 1

```bash
# Run task-creation tests together:
Task: "Add failing API tests in backend/tests/api/tasks-create.api.test.js"
Task: "Add frontend component tests in frontend/tests/unit/TaskForm.test.jsx"

# Once the shared validation and storage services exist, implement create logic with validation centralized in validationService.js and orchestration in taskService.js:
Task: "Implement create-task validation in backend/src/services/validationService.js"
Task: "Implement create-task orchestration in backend/src/services/taskService.js"
Task: "Add the POST route in backend/src/routes/tasks.js"
Task: "Implement the create form in frontend/src/components/TaskForm.jsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational validation and persistence.
3. Complete Phase 3: User Story 1 (task creation and safe rejection).
4. Stop and validate the create flow independently before proceeding.
5. Extend to User Stories 2-7 in priority order only after the create path is verified.

### Incremental Delivery

1. Deliver the backend persistence, validation, and create story first.
2. Add retrieval and update flows next using the same shared validation and storage services.
3. Extend the frontend incrementally within each relevant user story as the backend API becomes available, keeping the UI aligned with the approved task-management features.
4. Add delete, tag filtering, sorting, and status transitions as related increments within their user stories, then finish with cross-cutting validation, security review, and harness evidence capture.

## Suggested MVP Scope

The recommended initial minimum viable scope is **User Story 1** plus the foundational storage, validation, and project setup required for deterministic persistence. Once that path is validated, deliver User Stories 2-7 in priority order.

## Format validation

- Every task follows the required checklist format: `- [ ] T### ...`
- Task IDs remain sequential and unique.
- Story tasks include the relevant `[USx]` label and file path.
- Setup, foundation, and harness tasks remain story-neutral and do not claim implementation beyond the approved scope.
- The generated task list preserves the seven approved user stories and the MVP-first sequencing required by the assignment.
