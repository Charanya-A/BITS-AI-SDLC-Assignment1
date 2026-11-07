import { PRIORITY_LEVELS, STATUS_LEVELS, TASK_DEFAULTS } from '../models/taskModel.js';

const EMPTY_PATCH_ERROR = 'Request body must contain at least one supported field.';
const ALLOWED_CREATE_KEYS = new Set(['title', 'description', 'priority', 'tags', 'status']);
const ALLOWED_UPDATE_KEYS = new Set(['title', 'description', 'priority', 'tags']);

function throwValidationError(message) {
  const error = new Error(message);
  error.code = 'VALIDATION_ERROR';
  throw error;
}

function normalizedString(value, fieldName, { allowEmpty = false, maxLength = null } = {}) {
  if (typeof value !== 'string') {
    throwValidationError(`${fieldName} must be a string.`);
  }

  const trimmed = value.trim();
  if (!allowEmpty && trimmed.length === 0) {
    throwValidationError(`${fieldName} cannot be empty.`);
  }
  if (maxLength !== null && trimmed.length > maxLength) {
    throwValidationError(`${fieldName} exceeds ${maxLength} characters.`);
  }
  return trimmed;
}

export function sanitizeTags(tags) {
  if (tags === undefined) return [...TASK_DEFAULTS.tags];
  if (!Array.isArray(tags)) throwValidationError('tags must be an array of strings.');

  const cleaned = tags.map((tag) => {
    if (typeof tag !== 'string') throwValidationError('Each tag must be a non-empty string.');
    const trimmed = tag.trim();
    if (!trimmed) throwValidationError('Each tag must be a non-empty string.');
    return trimmed;
  });

  return cleaned;
}

export function validateCreateTaskInput(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throwValidationError('Task payload must be an object.');
  }

  const suppliedKeys = Object.keys(input);
  for (const key of suppliedKeys) {
    if (!ALLOWED_CREATE_KEYS.has(key)) {
      throwValidationError(`Unsupported field: ${key}`);
    }
  }

  const title = normalizedString(input.title, 'title', { allowEmpty: false, maxLength: 120 });
  if (title.length < 1) {
    throwValidationError('title must be between 1 and 120 characters after trimming.');
  }

  const description = normalizedString(input.description, 'description', { allowEmpty: true, maxLength: 2000 });
  const priority = input.priority;
  if (!PRIORITY_LEVELS.includes(priority)) {
    throwValidationError(`priority must be one of: ${PRIORITY_LEVELS.join(', ')}`);
  }

  const tags = sanitizeTags(input.tags ?? []);
  const status = input.status ?? TASK_DEFAULTS.status;
  if (!STATUS_LEVELS.includes(status)) {
    throwValidationError(`status must be one of: ${STATUS_LEVELS.join(', ')}`);
  }

  return {
    title,
    description,
    priority,
    tags,
    status,
  };
}

export function validateUpdateTaskInput(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throwValidationError('Update payload must be a non-empty object.');
  }

  const suppliedKeys = Object.keys(input);
  if (suppliedKeys.length === 0) throwValidationError(EMPTY_PATCH_ERROR);

  for (const key of suppliedKeys) {
    if (!ALLOWED_UPDATE_KEYS.has(key)) {
      throwValidationError(`Unsupported field: ${key}`);
    }
  }

  const sanitized = { ...input };

  if (sanitized.title !== undefined) {
    const title = normalizedString(sanitized.title, 'title', { allowEmpty: false, maxLength: 120 });
    if (title.length < 1) {
      throwValidationError('title must be between 1 and 120 characters after trimming.');
    }
    sanitized.title = title;
  }

  if (sanitized.description !== undefined) {
    sanitized.description = normalizedString(sanitized.description, 'description', { allowEmpty: true, maxLength: 2000 });
  }

  if (sanitized.priority !== undefined && !PRIORITY_LEVELS.includes(sanitized.priority)) {
    throwValidationError(`priority must be one of: ${PRIORITY_LEVELS.join(', ')}`);
  }

  if (sanitized.tags !== undefined) {
    sanitized.tags = sanitizeTags(sanitized.tags);
  }

  return sanitized;
}

export function validateStatusTransition(currentStatus, nextStatus) {
  const allowedTransitions = {
    PENDING: ['IN_PROGRESS'],
    IN_PROGRESS: ['COMPLETED'],
    COMPLETED: [],
  };

  if (!STATUS_LEVELS.includes(currentStatus)) {
    throwValidationError(`Current status is invalid: ${currentStatus}`);
  }

  if (!STATUS_LEVELS.includes(nextStatus)) {
    const error = new Error(`status must be one of: ${STATUS_LEVELS.join(', ')}`);
    error.code = 'INVALID_STATUS_TRANSITION';
    throw error;
  }

  if (currentStatus === nextStatus) {
    const error = new Error('Status change repeats the current state.');
    error.code = 'INVALID_STATUS_TRANSITION';
    throw error;
  }

  if (!allowedTransitions[currentStatus]?.includes(nextStatus)) {
    const error = new Error(`Invalid status transition: ${currentStatus} -> ${nextStatus}`);
    error.code = 'INVALID_STATUS_TRANSITION';
    throw error;
  }

  return true;
}

export function validateStatusBody(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throwValidationError('Status payload must be an object.');
  }

  const keys = Object.keys(input);
  if (keys.length !== 1 || !('status' in input)) {
    throwValidationError('Status update request must contain exactly one status field.');
  }

  const status = input.status;
  if (!STATUS_LEVELS.includes(status)) {
    throwValidationError(`status must be one of: ${STATUS_LEVELS.join(', ')}`);
  }

  return { status };
}

export function ensureTaskId(id) {
  if (!id || typeof id !== 'string') throwValidationError('Task id is required.');
  return id;
}
