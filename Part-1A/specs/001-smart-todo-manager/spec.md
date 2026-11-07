# Feature Specification: Smart Todo & Task Manager

**Feature Branch**: `001-smart-todo-manager`

**Created**: 2026-11-05

**Status**: Draft

**Input**: Product vision and requirements for a deterministic task management application that allows a single user to organize tasks, assign priorities and tags, track status, and persist task data across application restarts.

## Clarifications

### Session 2026-11-05
- Q: What is the deterministic tie-break rule for tasks with the same priority? → A: Display order is HIGH, MEDIUM, LOW; tasks with equal priority are ordered by createdAt ascending, then by task ID in ascending lexicographical order.
- Q: What are the supported task status values and transitions? → A: Supported statuses are PENDING, IN_PROGRESS, and COMPLETED; allowed transitions are PENDING -> IN_PROGRESS and IN_PROGRESS -> COMPLETED; all other transitions are rejected.
- Q: What validation and API contract details are required before implementation approval? → A: Title is required (1–120 trimmed characters), description is required as a field but may be empty (max 2000 characters), tags default to an empty array and must be non-empty trimmed strings when supplied, priority is required and must be LOW, MEDIUM, or HIGH, status defaults to PENDING at creation, and the server generates ID, createdAt, and updatedAt; API endpoints are POST /api/tasks, GET /api/tasks, GET /api/tasks/:id, PATCH /api/tasks/:id, PATCH /api/tasks/:id/status, and DELETE /api/tasks/:id with defined request and response schemas in the API section.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a task reliably (Priority: P1)

As a user, I want to create a task with the required information so that it is tracked and persisted for future review.

**Why this priority**: Task creation is the primary user flow and the foundation for all downstream retrieval, update, deletion, and filtering behaviors.

**Independent Test**: A user can submit a complete task payload and verify that the task is stored with a stable ID; a malformed payload is rejected without changing stored data.

**Acceptance Scenarios**:

1. **Given** a task list that is empty or contains other tasks, **When** a valid task is created with a title, description, priority, and optional tags, **Then** the system creates a task with a unique, stable ID and persists it.
2. **Given** a valid task creation request, **When** the task is retrieved by ID, **Then** the returned task includes the same values supplied during creation and defaults any omitted status to PENDING.
3. **Given** a malformed request that omits a required field or contains an invalid value, **When** the task is submitted, **Then** the create operation fails and the stored task list remains unchanged.
4. **Given** an existing persisted task list, **When** a create request fails validation, **Then** no unrelated task is added, removed, or modified.

---

### User Story 2 - View all tasks and individual tasks (Priority: P1)

As a user, I want to retrieve tasks by collection and by task ID so that I can review the current task state and specific details.

**Why this priority**: Task visibility is required to manage work effectively and to validate task persistence after restarts.

**Independent Test**: A user can list all tasks and read a specific task by ID, while an unknown ID returns a clear not-found response.

**Acceptance Scenarios**:

1. **Given** a persisted task list with multiple records, **When** the user requests all tasks, **Then** the system returns the full set of tasks in a deterministic and consistent order.
2. **Given** a valid task ID, **When** the user requests that single task, **Then** the system returns the exact matching task.
3. **Given** a task ID that does not exist, **When** the user requests the task, **Then** the system returns a not-found response and does not expose internal system details.
4. **Given** a malformed task ID, **When** the request is processed, **Then** the system rejects the request with an appropriate validation or not-found response.

---

### User Story 3 - Update permitted task fields without altering unrelated tasks (Priority: P1)

As a user, I want to update a task while preserving its identity and leaving unrelated tasks untouched so that task data remains accurate and consistent.

**Why this priority**: Updates are required for task maintenance, but they must be controlled to prevent accidental data corruption.

**Independent Test**: A user can update a task's permitted fields through the general task update endpoint and verify that the task ID stays constant while other tasks remain unchanged; status updates are handled through the dedicated endpoint.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** the user updates a permitted field such as title, description, tags, or priority using `PATCH /api/tasks/:id`, **Then** the task reflects the new value while retaining the same unique ID.
2. **Given** multiple tasks in storage, **When** one task is updated, **Then** the other tasks remain unchanged.
3. **Given** an invalid update payload, **When** the request is submitted, **Then** the system rejects the request and preserves the original persisted task record.
4. **Given** an update that attempts to modify the task ID or status through `PATCH /api/tasks/:id`, **When** the request is processed, **Then** the system rejects the change and the original task remains unmodified.
5. **Given** a status change request that includes a status field in `PATCH /api/tasks/:id`, **When** the request is processed, **Then** the system rejects the payload as an unsupported field and leaves the task unchanged because status updates must use `PATCH /api/tasks/:id/status`.

---

### User Story 4 - Delete a task safely (Priority: P1)

As a user, I want to delete a task using its ID so that outdated work is removed without affecting other tasks.

**Why this priority**: Deletion is a core content-management action and must be safe, deterministic, and recoverable through validation.

**Independent Test**: A user can delete an existing task and verify the task is removed; deleting a missing task returns a not-found response without altering other tasks.

**Acceptance Scenarios**:

1. **Given** an existing task in the task list, **When** the user deletes it using its ID, **Then** the task is removed and the remaining tasks remain unchanged.
2. **Given** a task ID that does not exist, **When** the user attempts to delete it, **Then** the system returns an appropriate not-found response.
3. **Given** a request that includes a malformed or missing ID, **When** the delete request is processed, **Then** the operation is rejected and no task data is changed.
4. **Given** multiple tasks, **When** one is deleted, **Then** all unrelated tasks remain intact.

---

### User Story 5 - Manage tags and filter by tag (Priority: P1)

As a user, I want to assign multiple tags to tasks and filter by tag so that I can quickly find relevant work items.

**Why this priority**: Tagging and filtering improve task organization and support repeatable retrieval based on classification.

**Independent Test**: A user can assign tags to tasks and filter the task list using a tag value, while case-insensitive matching and missing matches behave correctly.

**Acceptance Scenarios**:

1. **Given** a task with one or more tags, **When** the user filters tasks by an exact tag value, **Then** all tasks matching that tag are returned.
2. **Given** tasks tagged with mixed-case values such as "Work" and "work", **When** the user filters by a tag using a different case, **Then** matching is case-insensitive and the same tasks are returned.
3. **Given** a task without the selected tag, **When** the user applies a tag filter, **Then** the task is excluded from the filtered result.
4. **Given** a filter request with no matching tasks, **When** the task list is processed, **Then** the system returns an empty result rather than an error.

---

### User Story 6 - Sort tasks by priority deterministically (Priority: P1)

As a user, I want tasks to be sorted by priority in a consistent order so that the most urgent work appears first and the ordering is repeatable.

**Why this priority**: Deterministic sorting makes the application predictable and testable, and it supports decision-making for the user.

**Independent Test**: A user can sort tasks by priority and observe a repeatable order even when multiple tasks share the same priority.

**Acceptance Scenarios**:

1. **Given** a set of tasks with different priority values, **When** the user requests a priority-sorted view, **Then** the tasks are ordered according to the defined sequence HIGH, MEDIUM, LOW.
2. **Given** two or more tasks with the same priority, **When** the user requests a priority-sorted view, **Then** the tasks are ordered by createdAt ascending and, if createdAt values are equal, by task ID in ascending lexicographical order.
3. **Given** a valid priority sort request, **When** the data is sorted, **Then** the persisted task records remain unchanged and only the view or response ordering is affected.
4. **Given** an unsupported priority value in a request, **When** the task is processed, **Then** the request is rejected and the stored data is not modified.

---

### User Story 7 - Manage task status with valid transitions (Priority: P1)

As a user, I want statuses to follow explicit rules so that task progress is accurate and invalid changes are rejected safely.

**Why this priority**: Status transitions are a high-risk area for data integrity and must be controlled to prevent invalid task progression.

**Independent Test**: A user can update a task to an allowed status and observe that invalid transitions are rejected without altering the original task data.

**Acceptance Scenarios**:

1. **Given** a task in PENDING, **When** the user advances it to IN_PROGRESS using the dedicated status endpoint, **Then** the transition is accepted and the task state changes to IN_PROGRESS.
2. **Given** a task in IN_PROGRESS, **When** the user advances it to COMPLETED using the dedicated status endpoint, **Then** the transition is accepted and the task state changes to COMPLETED.
3. **Given** a task in COMPLETED, **When** the user attempts to move it back to PENDING or IN_PROGRESS, **Then** the request is rejected with a clear error.
4. **Given** a task in PENDING, **When** the user submits a repeated status transition such as `PENDING -> PENDING` or a task in IN_PROGRESS submits `IN_PROGRESS -> IN_PROGRESS`, **Then** the request is rejected with HTTP 409 and `INVALID_STATUS_TRANSITION`, and the persisted task data remains unchanged.
5. **Given** a task with a status value that is not supported by the application, **When** the task is processed, **Then** the system rejects the change and the original stored task remains unchanged.
6. **Given** an invalid status transition request, **When** the update is submitted, **Then** the original task record is preserved and no partial write occurs.

---

### Edge Cases

- What happens when the JSON persistence file is missing, unreadable, malformed, or empty at startup?
- What happens when task IDs are duplicated in the persisted file or when a request uses a malformed task ID?
- What happens when a task update includes unsupported values for tags, priority, or status?
- What happens when a persistence write fails after validation so that partial or inconsistent records must be avoided?
- What happens when a task is filtered using a tag that exists only with different casing?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a user to create a task with a title, description, priority, optional tags, and an optional status that defaults to PENDING.
- **FR-002**: The system MUST assign every task a unique, stable ID that remains unchanged during updates and is used to locate the task for retrieval, update, and deletion.
- **FR-003**: The system MUST validate required fields and valid values on the backend before persisting a task.
- **FR-004**: The system MUST reject invalid task creation requests without modifying the stored data.
- **FR-005**: The system MUST allow a user to retrieve all tasks and an individual task by ID.
- **FR-006**: The system MUST return an appropriate not-found response when a requested task ID does not exist.
- **FR-007**: The system MUST allow a user to update permitted task fields while preserving the original task ID.
- **FR-008**: The system MUST reject invalid changes without corrupting persisted data and without altering unrelated tasks.
- **FR-009**: The system MUST allow a user to delete a task by ID.
- **FR-010**: The system MUST return a not-found response when a delete request references an unknown task ID.
- **FR-011**: The system MUST preserve unrelated tasks when a single task is updated or deleted.
- **FR-012**: The system MUST support multiple tags per task and case-insensitive tag-based filtering.
- **FR-013**: The system MUST exclude tasks that do not match the selected tag from the filtered result.
- **FR-014**: The system MUST support three priority levels: LOW, MEDIUM, and HIGH.
- **FR-015**: The system MUST provide deterministic priority sorting using the order HIGH, MEDIUM, LOW, with equal priorities ordered by createdAt ascending and then by task ID in ascending lexicographical order.
- **FR-016**: The system MUST sort tasks without modifying the persisted task records.
- **FR-017**: The system MUST support the statuses PENDING, IN_PROGRESS, and COMPLETED.
- **FR-018**: The system MUST define and enforce explicitly permitted status transitions: PENDING -> IN_PROGRESS and IN_PROGRESS -> COMPLETED.
- **FR-019**: The system MUST reject invalid status transitions with a clear error and leave the original task unchanged.
- **FR-020**: The system MUST persist tasks in a local JSON file so that data remains available after an application restart.
- **FR-021**: The system MUST maintain a documented and consistent task schema with a unique ID for every task.
- **FR-022**: The system MUST handle missing, unreadable, or malformed storage files safely without corrupting existing records.
- **FR-023**: The system MUST validate inputs on the backend and reject malformed requests before any data write occurs.
- **FR-024**: The system MUST return appropriate HTTP status codes for successful and unsuccessful operations.
- **FR-025**: The system MUST provide consistent error response structures for validation, not-found, and persistence failures.
- **FR-026**: The system MUST avoid exposing filesystem paths, secrets, or internal stack traces to clients.
- **FR-027**: The system MUST maintain responsibility boundaries between frontend, backend, and persistence logic.
- **FR-028**: The system MUST provide clear validation and error messages and remain maintainable and testable.
- **FR-029**: The system MUST include reproducible setup and execution instructions for running validation and verifying the expected behavior.
- **FR-030**: The system MUST provide test coverage for every approved functional requirement, including positive, negative, and boundary conditions.
- **FR-031**: The system MUST generate ID, createdAt, and updatedAt values on the server and reject client attempts to modify these fields.
- **FR-032**: The system MUST accept title values trimmed to 1-120 characters, description values that are required as a field but may be empty strings up to 2000 characters, and tags as a list of trimmed non-empty strings or an empty array by default.
- **FR-033**: The system MUST use a dedicated status endpoint for status changes, while ordinary task updates via `PATCH /api/tasks/:id` MUST allow only title, description, tags, and priority.
- **FR-034**: The system MUST initialize a valid empty task store when the JSON file is missing or empty, and MUST stop startup with a clear error when the existing file contains malformed JSON or cannot be read without overwriting the original file.
- **FR-035**: The system MUST use a safe write strategy so failed writes do not leave partially written JSON data and MUST return the documented safe persistence error response for runtime read/write failures without exposing internal paths or stack traces.

### Data and Persistence Requirements

- The application MUST persist tasks to a local JSON file rather than using an external database.
- Each task record MUST include a unique ID and a consistent schema that defines the required fields and allowed values.
- Task data MUST remain available after application restart.
- Invalid requests MUST NOT corrupt the persisted data or create partial writes.
- Missing, unreadable, or malformed storage files MUST be handled safely and explicitly.
- Persistence operations MUST fail clearly and leave the stored file in a consistent state.
- Malformed or unreadable existing JSON at application startup MUST stop startup with a clear error and preserve the original file.
- Runtime read or write failures MUST return the documented safe persistence error response without exposing internal paths or stack traces.
- Failed writes MUST not leave partially written JSON data behind; persistence writes MUST use a temporary file and atomic replacement, and all writes within the single Node.js application process MUST be serialized to avoid overlapping writes corrupting the task store.
- Cross-process synchronization is out of scope; the requirement is limited to safe single-process coordination.

### API Requirements

- The application MUST expose RESTful endpoints for creating, reading, updating, deleting, filtering, and status-changing tasks.
- The API MUST define request and response formats for all endpoint behaviors.
- The API MUST return the correct HTTP status code for each success, validation failure, malformed request, not-found condition, and persistence failure.
- The API MUST provide a consistent error response structure that excludes filesystem path details, credentials, and internal stack traces.
- The API MUST distinguish `VALIDATION_ERROR` from `MALFORMED_REQUEST` and apply the appropriate HTTP 400 response to each.
- The API MUST validate all incoming data on the backend before processing.

### API Contract (Finalized)

- **Task Response Object**: A task resource MUST have the following server-managed and validated fields:
  - `id` (string, required, unique, stable): RFC 4122 UUID v4 format; example `3f5d1f3e-4d12-4a2d-9e08-f0ad0d5c1b2a`
  - `title` (string, required, trimmed, 1-120 chars)
  - `description` (string, required as a field, may be empty, maximum 2000 chars)
  - `priority` (string enum: `LOW`, `MEDIUM`, `HIGH`)
  - `tags` (string array, optional, defaults to `[]`, each entry trimmed and non-empty)
  - `status` (string enum: `PENDING`, `IN_PROGRESS`, `COMPLETED`, defaults to `PENDING` on creation)
  - `createdAt` (string, required, UTC ISO 8601 timestamp in the format `YYYY-MM-DDTHH:mm:ss.sssZ`)
  - `updatedAt` (string, required, UTC ISO 8601 timestamp in the format `YYYY-MM-DDTHH:mm:ss.sssZ`)
- **Client Restrictions**: Clients MUST NOT send `id`, `createdAt`, or `updatedAt` values. The server MUST generate and manage those values. Clients MUST NOT update `status` via `PATCH /api/tasks/:id`; status must be changed only through `PATCH /api/tasks/:id/status`.
- **Error Response Schema**:
  - `{ "error": { "code": "VALIDATION_ERROR | MALFORMED_REQUEST | NOT_FOUND | INVALID_STATUS_TRANSITION | PERSISTENCE_ERROR", "message": "human-readable summary", "details": { ...optional field-level details... } } }`
  - `details` is optional and may be omitted for simple errors; when present, it must describe only the relevant field or request issue and must not expose internal filesystem paths, secrets, or stack traces.
- **HTTP Status and Error Code Mapping**:
  - `400 BAD_REQUEST` with `VALIDATION_ERROR` for syntactically valid JSON that contains invalid field values, missing required fields, empty PATCH request bodies, or unsupported fields.
  - `400 BAD_REQUEST` with `MALFORMED_REQUEST` for invalid JSON syntax or structurally malformed request bodies that cannot be parsed or processed.
  - `404 NOT_FOUND` with `NOT_FOUND` when the target task does not exist.
  - `409 CONFLICT` with `INVALID_STATUS_TRANSITION` when a status change is disallowed or repeats the current status.
  - `500 INTERNAL_SERVER_ERROR` with `PERSISTENCE_ERROR` when a runtime JSON read or write failure occurs after validation, or when the JSON store cannot be read or written safely.
- **Endpoint Contract**:
  - `POST /api/tasks`
    - Request body: `{ "title": "string", "description": "string", "priority": "LOW|MEDIUM|HIGH", "tags": ["string"], "status": "PENDING|IN_PROGRESS|COMPLETED" }`
    - Validation: `title` is required, trimmed to 1-120 chars; `description` is required as a field and may be empty; `priority` is required; `tags`, if supplied, must be an array of non-empty trimmed strings; default `tags` to `[]`; default `status` to `PENDING`; reject any client-supplied `id`, `createdAt`, or `updatedAt` values.
    - Success: `201 CREATED` returning `{ "data": task }` where `task` is the complete task object.
  - `GET /api/tasks`
    - Query params: optional `tag` and optional `sort=priority`.
    - `tag` filter: case-insensitive comparison against task tags; tasks without a matching tag are excluded.
    - `sort=priority`: order is `HIGH`, then `MEDIUM`, then `LOW`; equal priority tasks are ordered by `createdAt` ascending and then by `id` asc. Sorting must not modify stored task records or persisted order.
    - Success: `200 OK` returning `{ "data": [tasks] }`.
  - `GET /api/tasks/:id`
    - Success: `200 OK` returning `{ "data": task }`.
    - Not found: `404 NOT_FOUND` with the standard error schema.
  - `PATCH /api/tasks/:id`
    - Request body: any non-empty object containing one or more of `title`, `description`, `priority`, and `tags`.
    - Validation: reject an empty request body, unknown fields, or attempts to change `id`, `createdAt`, `updatedAt`, or `status`; preserve unspecified fields; update `updatedAt` only on successful persistence.
    - Success: `200 OK` returning `{ "data": updatedTask }`.
    - Validation failure: `400 BAD_REQUEST` with the standard error schema.
    - Not found: `404 NOT_FOUND` with the standard error schema.
  - `PATCH /api/tasks/:id/status`
    - Request body: `{ "status": "IN_PROGRESS" }` or another supported value for an allowed transition.
    - Supported transitions: `PENDING -> IN_PROGRESS` and `IN_PROGRESS -> COMPLETED`.
    - All other transitions, including repeating the current status, are rejected.
    - A rejected transition must leave the original persisted task unchanged and must return `409 CONFLICT` with `INVALID_STATUS_TRANSITION`.
    - Success: `200 OK` returning `{ "data": updatedTask }`.
  - `DELETE /api/tasks/:id`
    - Deletes the task matching the supplied ID.
    - Success: `204 NO_CONTENT` with no response body.
    - Not found: `404 NOT_FOUND` with the standard error schema.
- **Status Transition Rule**: The only supported server-accepted transitions are `PENDING -> IN_PROGRESS` and `IN_PROGRESS -> COMPLETED`. Requests that repeat the current state or attempt any other transition are rejected without modifying persisted data.
- **Sorting Rule**: Priority sorting MUST use the order `HIGH`, then `MEDIUM`, then `LOW`; equal-priority tasks MUST be ordered by `createdAt` ascending and then by `id` in ascending lexicographical order.
- **Persistence Rule**: The JSON file is the sole persistence mechanism. Missing or empty files initialize as an empty task collection. Malformed or unreadable existing JSON must not be silently overwritten or reset. Safe writes MUST use a temporary file and atomic replacement so that failed writes do not leave partial JSON data. All writes within the single Node.js application process MUST be serialized to prevent overlapping writes from corrupting data; cross-process locking is out of scope.

### Non-Functional Requirements

- The frontend, backend, and persistence responsibilities MUST remain separate and maintainable.
- The application MUST provide clear validation and error messages that support deterministic testing.
- The application MUST avoid exposing secrets, internal errors, or filesystem details through client-facing responses.
- The application MUST remain maintainable, reproducible, and testable using repeatable inputs and expected outputs.
- Setup and execution instructions MUST be clear enough to reproduce validation and acceptance checks.

### Out of Scope

- User authentication and authorization.
- Multi-user collaboration.
- Email, SMS, or push notifications.
- Recurring tasks.
- Cloud synchronization.
- External database integration.

### Key Entities *(include if feature involves data)*

- **Task**: Represents a single work item and includes a unique stable ID, title, description, tags, priority, and status.
- **Tag**: Represents a user-defined label used to classify and filter tasks.
- **Priority**: Represents urgency and must be limited to LOW, MEDIUM, or HIGH.
- **Status**: Represents the current lifecycle state of the task and must be limited to PENDING, IN_PROGRESS, and COMPLETED.
- **Task Store**: Represents the local JSON file used to persist tasks across application restarts.

## Acceptance Criteria *(mandatory)*

### AC-US1-01: Valid task creation succeeds
- **Preconditions**: The task store is available and writable.
- **Input/Action**: Send a valid task creation request containing a trimmed title (1-120 characters), a description field that may be empty but no longer than 2000 characters, a required priority value, and any optional tags array.
- **Expected Result**: The system creates a task with a unique, stable ID, server-generated timestamps, and a default status of PENDING when status is omitted; the created task is returned in a success response.
- **Failure Behavior**: If any required field is missing or invalid, the request fails without changing stored data.

### AC-US1-02: Invalid task creation does not modify stored data
- **Preconditions**: The task store contains one or more existing tasks.
- **Input/Action**: Submit a task creation request with a missing title, invalid priority, a malformed tag, or a client-provided ID or timestamp field.
- **Expected Result**: The system rejects the request and returns a validation error.
- **Failure Behavior**: The stored tasks remain identical before and after the failed request.

### AC-US1-03: Task ID stability is enforced
- **Preconditions**: A task already exists in storage.
- **Input/Action**: Retrieve or update the task by ID.
- **Expected Result**: The system uses the same ID consistently and does not allow the ID, createdAt, or updatedAt values to be changed by clients.
- **Failure Behavior**: Any attempt to alter these server-generated fields is rejected without modifying persisted data.

### AC-US2-01: List all tasks
- **Preconditions**: At least one task exists in storage.
- **Input/Action**: Request the collection of all tasks.
- **Expected Result**: The system returns all persisted tasks in a deterministic and consistent response.
- **Failure Behavior**: If the store cannot be read, the system returns a clear error without exposing system details.

### AC-US2-02: Retrieve an individual task by ID
- **Preconditions**: A valid task exists in storage.
- **Input/Action**: Request a task using its ID.
- **Expected Result**: The system returns exactly the matching task record.
- **Failure Behavior**: If the ID is unknown, the system returns a not-found response.

### AC-US2-03: Unknown task ID is handled safely
- **Preconditions**: The task ID is not present in the store.
- **Input/Action**: Request a task with that ID.
- **Expected Result**: The system returns a not-found response with a consistent error structure.
- **Failure Behavior**: The response does not disclose filesystem details, stack traces, or other internal data.

### AC-US3-01: Permitted field updates succeed
- **Preconditions**: A valid task exists in storage.
- **Input/Action**: Update a permitted field such as title, description, priority, or tags by calling `PATCH /api/tasks/:id`.
- **Expected Result**: The system updates only the requested field and preserves the task ID; status changes must be performed through `PATCH /api/tasks/:id/status`.
- **Failure Behavior**: If the field is invalid or if a status field is sent through the general update endpoint, the request fails and the original record remains unchanged.

### AC-US3-02: Unrelated tasks are not modified
- **Preconditions**: At least two tasks exist in storage.
- **Input/Action**: Update one task.
- **Expected Result**: Only the selected task changes; all other task records remain exactly as they were.
- **Failure Behavior**: Any unintended modification to another task is considered a failure.

### AC-US3-03: Invalid updates are rejected
- **Preconditions**: A valid task exists in storage.
- **Input/Action**: Submit an update containing invalid values, missing required fields, or a disallowed change such as a modified ID.
- **Expected Result**: The system rejects the update and preserves the original persisted data.
- **Failure Behavior**: No partial update is committed.

### AC-US4-01: Delete an existing task succeeds
- **Preconditions**: A valid task exists in storage.
- **Input/Action**: Delete the task using its ID.
- **Expected Result**: The selected task is removed and the system returns a successful delete response.
- **Failure Behavior**: If the task ID is invalid or missing, the request fails without modifying stored data.

### AC-US4-02: Delete an unknown task returns not found
- **Preconditions**: The requested task ID does not exist in storage.
- **Input/Action**: Submit a delete request for that ID.
- **Expected Result**: The system returns a not-found response and leaves all tasks unchanged.
- **Failure Behavior**: The request must not create records or alter any unrelated task.

### AC-US5-01: Tag assignment and retrieval
- **Preconditions**: A valid task exists.
- **Input/Action**: Add one or more tags to the task and retrieve tasks afterwards.
- **Expected Result**: The task carries all associated tags and the tags are returned in the response data.
- **Failure Behavior**: Missing or malformed tag data is rejected without persisting corrupt values.

### AC-US5-02: Tag filtering is case-insensitive
- **Preconditions**: The task store contains tasks with tags in mixed casing.
- **Input/Action**: Request a filter using a different case than the stored tag value.
- **Expected Result**: Matching is case-insensitive and all relevant tasks are included in the filtered result.
- **Failure Behavior**: A request with no matching tags returns an empty result rather than incorrect matches.

### AC-US5-03: Non-matching tags are excluded
- **Preconditions**: The task store contains tasks with different tags.
- **Input/Action**: Filter by a tag that matches only a subset of tasks.
- **Expected Result**: Only tasks with a matching tag are included in the result.
- **Failure Behavior**: Tasks without that tag must not appear in the filtered response.

### AC-US6-01: Priority ordering is deterministic
- **Preconditions**: The task store contains tasks with different priorities.
- **Input/Action**: Request the task list sorted by priority.
- **Expected Result**: Tasks are returned in the order HIGH, MEDIUM, LOW.
- **Failure Behavior**: Invalid priority values are rejected and do not alter the stored data.

### AC-US6-02: Equal-priority tie-breaking is consistent
- **Preconditions**: Two or more tasks have the same priority.
- **Input/Action**: Request a priority-sorted list.
- **Expected Result**: Tasks with equal priority are ordered by createdAt ascending, and if createdAt values are equal, by task ID in ascending lexicographical order.
- **Failure Behavior**: The result ordering must remain deterministic and not depend on storage ordering alone.

### AC-US6-03: Sorting does not change persisted records
- **Preconditions**: The task store has multiple tasks.
- **Input/Action**: Sort tasks by priority for display or retrieval.
- **Expected Result**: The storage file and task records remain unchanged; only the response order changes.
- **Failure Behavior**: A sorting request must never rewrite persisted records.

### AC-US7-01: Valid status transitions succeed
- **Preconditions**: A task exists in PENDING or IN_PROGRESS.
- **Input/Action**: Submit a status change request to the dedicated status endpoint using an allowed transition: PENDING -> IN_PROGRESS or IN_PROGRESS -> COMPLETED.
- **Expected Result**: The status changes only if it is an allowed transition in the defined status model.
- **Failure Behavior**: Unsupported or invalid transitions fail without changing the stored task.

### AC-US7-02: Invalid transitions are rejected
- **Preconditions**: A task exists in a valid status.
- **Input/Action**: Attempt a disallowed transition such as COMPLETED to PENDING or PENDING to COMPLETED.
- **Expected Result**: The system rejects the request with a clear error and preserves the original task state.
- **Failure Behavior**: No partial or corrupted status change is stored.

### AC-US7-03: Repeated transitions are rejected
- **Preconditions**: A task exists in PENDING or IN_PROGRESS.
- **Input/Action**: Submit a request to the dedicated status endpoint using the same status value as the current task state, such as `PENDING -> PENDING` or `IN_PROGRESS -> IN_PROGRESS`.
- **Expected Result**: The API returns HTTP 409 with `INVALID_STATUS_TRANSITION`, and the persisted task remains unchanged.
- **Failure Behavior**: No repeated transition is accepted or partially applied.

### AC-US7-04: Unsupported status values are rejected
- **Preconditions**: A valid task exists.
- **Input/Action**: Submit a task creation, ordinary update, or status-change request containing a status value outside the supported set.
- **Expected Result**: The system rejects the request and leaves the task store unchanged.
- **Failure Behavior**: No invalid value is written to storage.

### AC-Data-01: Persistence remains available across restarts
- **Preconditions**: The task store contains at least one task and the application has been stopped.
- **Input/Action**: Restart the application and load task data from the local JSON file.
- **Expected Result**: The persisted tasks remain available after restart with the same contents and IDs.
- **Failure Behavior**: Missing or malformed storage is handled safely and does not silently corrupt the task data.

### AC-Data-02: Malformed storage is handled safely
- **Preconditions**: The persistence file is missing, unreadable, malformed, or empty.
- **Input/Action**: Start the application and attempt to read the task data.
- **Expected Result**: Missing or empty files initialize a valid empty task store; malformed or unreadable existing files stop startup with a clear error and preserve the original file rather than overwriting or silently resetting it.
- **Failure Behavior**: The system must not exhibit silent data loss or write a malformed file.

### AC-Data-03: Runtime persistence failures are safe and explicit
- **Preconditions**: The application has started successfully and then encounters a runtime read or write failure while accessing the JSON task store.
- **Input/Action**: Trigger a failure such as a read error, write error, or atomic replacement failure during task mutation or retrieval.
- **Expected Result**: The API returns the documented `PERSISTENCE_ERROR` response with a safe error structure, and the system does not expose internal paths, stack traces, or sensitive filesystem details.
- **Failure Behavior**: Failed writes do not leave partially written JSON data behind.

### AC-API-01: REST endpoints follow expected behaviors
- **Preconditions**: The API is running.
- **Input/Action**: Call the create, list, get-by-ID, update, delete, filter, and status-change endpoints.
- **Expected Result**: Each endpoint responds with the correct success or failure behavior and status code for the given input, including 201 for create, 200 for reads and update success, 204 for delete success, 400 for validation or malformed request issues, 404 for missing tasks, 409 for invalid status transitions, and 500 for persistence failures.
- **Failure Behavior**: Validation, malformed-request, not-found, invalid-status-transition, and persistence issues use the documented error structures and codes.

### AC-API-02: Error responses are consistent and safe
- **Preconditions**: The API receives validation, malformed-request, not-found, invalid-status-transition, or persistence-failure requests.
- **Input/Action**: Trigger validation, syntax, status, or storage errors.
- **Expected Result**: The API returns a consistent error structure without exposing secrets, filesystem paths, or internal stack traces.
- **Failure Behavior**: Client-facing errors remain informative but not sensitive.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can create, retrieve, update, delete, filter, and manage task status for all supported scenarios without data loss.
- **SC-002**: 100% of mandatory acceptance criteria pass in the deterministic automated test suite before final acceptance.
- **SC-003**: All critical data-integrity, validation, security, and status-transition tests pass before final acceptance.
- **SC-004**: Invalid inputs, malformed storage, and disallowed status transitions are rejected without corrupting persisted JSON data.
- **SC-005**: Tasks remain available after application restarts and continue to satisfy the documented schema and unique ID requirements.
- **SC-006**: No secrets, filesystem paths, or internal stack traces are exposed through API responses, and no unresolved critical security findings remain at final approval.

## Assumptions

- The application is intended for a single user working with a local task dataset and does not require authentication or multi-user coordination.
- The task list is persisted in a local JSON file and is expected to remain available across application restarts.
- Priority is constrained to LOW, MEDIUM, and HIGH; statuses are constrained to PENDING, IN_PROGRESS, and COMPLETED; and task ordering is deterministic by priority and a defined tie-break rule.
- `createdAt` is server-generated and monotonic across created tasks; when equal values occur, task ID order resolves the tie deterministically.
- Validation failures are expected to reject requests before any write occurs, preserving the integrity of the stored data.
- The application will initialize a valid empty store when the storage file is missing or empty and will stop with a clear error when an existing file is malformed or unreadable.

## Approved Baseline Decisions

- The deterministic priority order is HIGH, MEDIUM, LOW, with equal-priority tasks ordered by createdAt ascending and then by task ID in ascending lexicographical order.
- The supported status values are PENDING, IN_PROGRESS, and COMPLETED; only PENDING -> IN_PROGRESS and IN_PROGRESS -> COMPLETED are allowed.
- The task schema and REST request/response contract are defined in the API contract section above, and the server manages ID, createdAt, and updatedAt values.
- Missing or empty storage files initialize a valid empty task store; malformed or unreadable existing files stop startup with a clear error and preserve the original file.
- The baseline specification remains deliberately limited to the approved single-user, local, JSON-backed requirements and does not extend to multi-user or concurrent-write behavior.
