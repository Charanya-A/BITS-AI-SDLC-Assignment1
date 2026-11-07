import test from 'node:test';
import assert from 'node:assert/strict';
import { validateCreateTaskInput, validateUpdateTaskInput, validateStatusBody, validateStatusTransition } from '../../src/services/validationService.js';

test('validateCreateTaskInput trims title and accepts default status and tags', () => {
  const result = validateCreateTaskInput({
    title: '  Finish report  ',
    description: '',
    priority: 'HIGH',
    tags: [' college ', ' work '],
  });

  assert.equal(result.title, 'Finish report');
  assert.equal(result.description, '');
  assert.equal(result.status, 'PENDING');
  assert.deepEqual(result.tags, ['college', 'work']);
});

test('validateCreateTaskInput rejects invalid title and priority', () => {
  assert.throws(() => validateCreateTaskInput({ title: '   ', description: '', priority: 'CRITICAL' }), /title|priority/i);
  assert.throws(() => validateCreateTaskInput({ title: 'Task', description: 123, priority: 'LOW' }), /description must be a string/i);
});

test('validateUpdateTaskInput accepts only supported fields and rejects empty bodies', () => {
  assert.deepEqual(validateUpdateTaskInput({ title: 'Updated' }), { title: 'Updated' });
  assert.throws(() => validateUpdateTaskInput({}), /Request body must contain at least one supported field/i);
  assert.throws(() => validateUpdateTaskInput({ status: 'IN_PROGRESS' }), /Unsupported field: status/i);
});

test('validateStatusBody and validateStatusTransition enforce the approved transition rules', () => {
  assert.deepEqual(validateStatusBody({ status: 'IN_PROGRESS' }), { status: 'IN_PROGRESS' });
  assert.throws(() => validateStatusTransition('PENDING', 'PENDING'), /repeats the current state/i);
  assert.throws(() => validateStatusTransition('PENDING', 'COMPLETED'), /Invalid status transition/i);
  assert.equal(validateStatusTransition('PENDING', 'IN_PROGRESS'), true);
  assert.equal(validateStatusTransition('IN_PROGRESS', 'COMPLETED'), true);
});
