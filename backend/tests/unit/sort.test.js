import test from 'node:test';
import assert from 'node:assert/strict';
import { sortTasks } from '../../src/utils/sort.js';

test('sortTasks orders HIGH before MEDIUM before LOW and ties by createdAt then id', () => {
  const tasks = [
    { id: 'b-2', priority: 'LOW', createdAt: '2025-01-01T00:00:00.000Z' },
    { id: 'a-1', priority: 'HIGH', createdAt: '2025-01-01T00:00:00.000Z' },
    { id: 'b-1', priority: 'HIGH', createdAt: '2024-12-31T00:00:00.000Z' },
    { id: 'c-1', priority: 'MEDIUM', createdAt: '2025-01-01T00:00:00.000Z' },
  ];

  const sorted = sortTasks(tasks, { sort: 'priority' });
  assert.deepEqual(sorted.map((task) => task.id), ['b-1', 'a-1', 'c-1', 'b-2']);
});

test('sortTasks does not mutate the original array', () => {
  const tasks = [
    { id: 'task-2', priority: 'LOW', createdAt: '2025-01-01T00:00:00.000Z' },
    { id: 'task-1', priority: 'HIGH', createdAt: '2025-01-01T00:00:00.000Z' },
  ];

  const original = [...tasks];
  sortTasks(tasks, { sort: 'priority' });
  assert.deepEqual(tasks, original);
});
