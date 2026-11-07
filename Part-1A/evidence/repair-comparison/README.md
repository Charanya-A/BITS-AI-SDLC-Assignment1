# Part 1A – Historical Test Repair Evidence

## Purpose

This folder preserves textual comparisons between selected files from the available pre-repair backup and the corresponding current implementation.

## Evidence included

- `test-repair-diffs.txt`: Textual differences between the backup and current storage unit tests, and between the backup and current API tests.

## Findings

### 1. Storage unit-test isolation

The backup version created temporary directories but did not correctly configure the storage service to use the temporary file. Its malformed-JSON test therefore did not reliably exercise the file it created.

The current version introduces a temporary-store helper that configures the storage path, restores the previous path after the test, and cleans up the temporary directory. It also includes a write/read test.

### 2. API test isolation

The backup API tests used the shared application store path and reset that store before tests.

The current API tests configure a dedicated temporary store for the test suite and restore the previous path and clean up the temporary directory afterward. The current test file also contains additional API test coverage.

## Scope and provenance limitations

- The source files under `evidence/pre-repair-backup/` are a limited selected backup, not a complete initial-generation project snapshot.
- The available filesystem timestamps identify the dates on which the selected backup files were saved. They do not independently establish the exact time of every implementation or test activity.
- The comparisons show differences between the preserved backup files and the current files. They do not independently establish who made each change or the exact time each change was made.
- The backup `storageService.js` is byte-for-byte identical to the current `backend/src/services/storageService.js`; it is not evidence of a change to that service.
- The backup `tasks.json` differs from the current data file.
- This evidence supplements the implementation transcript and other harness records. It does not replace the missing complete, untouched initial-generation snapshot.

No historical source files or current implementation files were modified to create these comparisons.
