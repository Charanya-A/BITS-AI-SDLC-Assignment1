export function makeErrorResponse(code, message, details = undefined) {
  const error = new Error(message);
  error.code = code;
  if (details !== undefined) error.details = details;
  return error;
}

export function makeValidationError(message, details) {
  return makeErrorResponse('VALIDATION_ERROR', message, details);
}

export function makeMalformedRequestError(message, details) {
  return makeErrorResponse('MALFORMED_REQUEST', message, details);
}

export function makeNotFoundError(message) {
  return makeErrorResponse('NOT_FOUND', message);
}

export function makeInvalidStatusTransitionError(message) {
  return makeErrorResponse('INVALID_STATUS_TRANSITION', message);
}

export function makePersistenceError(message, details) {
  return makeErrorResponse('PERSISTENCE_ERROR', message, details);
}
