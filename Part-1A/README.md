
# Smart Todo Manager - Part 1A

A local task-management application built with React, Vite, Node.js and Express. Tasks are persisted in a local JSON file.

## Prerequisites

- Node.js and npm
- PowerShell
- Internet access for dependency installation, npm audits and OpenAPI linting
- Semgrep CLI for the security scan

## Project structure

- `backend/` - Express REST API and JSON file storage
- `frontend/` - React and Vite user interface
- `specs/` - Spec Kit specifications, plans, tasks and API contract
- `.harness/` - Automated verification script and run transcripts
- `evidence/` - Initial/final generation evidence, repair comparison and harness log

## Install dependencies

Open PowerShell in the `Part-1A` directory.

Backend:

    cd backend
    npm ci

Frontend (in a second terminal):

    cd frontend
    npm ci

## Run the application

Start the backend in one terminal:

    cd backend
    npm start

The API listens at:

    http://localhost:3000

Start the frontend in another terminal:

    cd frontend
    npm run dev

Open:

    http://localhost:5173

The frontend communicates with the backend at `http://localhost:3000/api`.

## Run tests

Backend tests:

    cd backend
    npm test

Frontend tests:

    cd frontend
    npm test

Frontend production build:

    cd frontend
    npm run build

## Run the complete verification harness

From the `Part-1A` directory:

    .\.harness\run-harness.ps1

The harness runs ten gates covering JavaScript syntax, backend and frontend tests, linting, production build, dependency audits, Semgrep scanning and OpenAPI contract validation.

The harness creates a timestamped transcript in `.harness/`.

## Verification evidence

See `evidence/harness-log.md` for the initial issues, root-cause analysis, repairs, final verification results, known limitations and final human decision.

The detailed final harness transcript is `evidence/final-verification-transcript.txt`.

The initial-generation evidence limitation is documented in `evidence/initial-generation/README.txt`.

## Data and limitations

Task data is stored locally in the backend JSON store. This is a local, single-user application and is not configured as a production multi-user service.
'@ | Set-Content -Path "$root\Part-1A\README.md" -Encoding utf8

