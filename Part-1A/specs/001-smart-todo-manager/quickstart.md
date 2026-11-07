# Quickstart Validation Guide

This guide describes the validation flow for the Smart Todo & Task Manager feature without embedding implementation code. It is intended to confirm that the approved specification is satisfied before moving to implementation.

## Prerequisites

- Node.js 24 LTS runtime installed
- npm available
- A local environment for the frontend and backend projects
- A writable working directory for the JSON task store

## Recommended Project Layout

```text
backend/
  src/
  tests/
frontend/
  src/
  tests/
```

## Planned setup commands

The intended project setup is intentionally simple and beginner-friendly:

```bash
# install backend dependencies
cd backend
npm install

# install frontend dependencies
cd ../frontend
npm install
```

## Planned startup commands

```bash
# run the backend API
cd backend
npm run dev

# in a second terminal, run the React frontend
cd frontend
npm run dev
```

## Planned validation commands

```bash
# backend validation
cd backend
npm run lint
npm test

# frontend validation
cd ../frontend
npm run lint
npm test
```

## Setup expectations

1. Install dependencies for the frontend and backend.
2. Configure the JSON task store path in the backend environment.
3. Confirm the backend can initialize an empty task store when the file is missing.
4. Ensure the frontend targets the backend REST API base URL.
5. Verify the backend runtime target is Node.js 24 LTS.

## Validation Checklist

### 1. Syntax and lint

- Run the frontend and backend syntax checks.
- Run linting with the project’s configured tooling.
- Confirm that no code-level errors block startup or test execution.

### 2. Unit tests

- Validate task schemas and sanitization helpers.
- Validate priority ordering logic and tie-break behavior.
- Validate status transition validation and rejection paths.
- Validate persistence helpers for atomic writes and empty-file initialization.

### 3. API/contract tests

- Create a task with valid payloads and verify `201` responses.
- Reject invalid create requests and verify `400` with the correct error code.
- Retrieve all tasks and a single task; verify `200` and `404` responses as required.
- Update a task with allowed fields; verify `200` and rejected unsupported modifications.
- Update status through the dedicated status endpoint; verify `200`, `409`, and unchanged persisted data.
- Delete tasks and verify `204` or `404` behavior.
- Verify malformed JSON and runtime persistence failures use the documented safe error schema.

### 4. End-to-end verification

- Start the backend and frontend.
- Create tasks with multiple priorities and tags.
- Sort by priority and verify deterministic order.
- Filter by tag in a case-insensitive manner.
- Verify persistence after restarting the backend.
- Verify invalid operations leave the original JSON file unchanged.

## Expected Outcomes

- All mandatory acceptance criteria pass.
- Required validation and persistence safeguards remain effective.
- No secrets, filesystem paths, or stack traces are exposed to the client.
- No unresolved critical security or integrity issues remain.
- The final implementation is built to the approved React + Vite, Node.js + Express, REST API, and JSON-only persistence requirements.
