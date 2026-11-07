
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {
  initializeStore,
  writeStore,
  safeReadStore,
} from '../../src/services/storageService.js';

async function withTempStore(fn) {
  const directory = await fs.mkdtemp(
    path.join(os.tmpdir(), 'todo-store-')
  );
  const storePath = path.join(directory, 'tasks.json');
  const previousPath = globalThis.__STORE_PATH__;

  globalThis.__STORE_PATH__ = storePath;

  try {
    await fn(storePath);
  } finally {
    if (previousPath === undefined) {
      delete globalThis.__STORE_PATH__;
    } else {
      globalThis.__STORE_PATH__ = previousPath;
    }

    await fs.rm(directory, { recursive: true, force: true });
  }
}

test('initializeStore creates an empty array when the file is missing', async () => {
  await withTempStore(async (storePath) => {
    const tasks = await initializeStore();

    assert.deepEqual(tasks, []);
    assert.equal(await fs.readFile(storePath, 'utf8'), '[]');
  });
});

test('initializeStore rejects malformed JSON without overwriting the existing file', async () => {
  await withTempStore(async (storePath) => {
    const malformedContent = '{ bad json';
    await fs.writeFile(storePath, malformedContent, 'utf8');

    await assert.rejects(
      initializeStore(),
      /malformed or unreadable/i
    );

    const existingContent = await fs.readFile(storePath, 'utf8');
    assert.equal(existingContent, malformedContent);
  });
});

test('writeStore persists tasks and safeReadStore returns the persisted tasks', async () => {
  await withTempStore(async () => {
    const tasks = [
      {
        id: 'test-task-1',
        title: 'Test task',
        description: '',
        priority: 'HIGH',
        tags: ['college'],
        status: 'PENDING',
        createdAt: '2026-11-05T12:00:00.000Z',
        updatedAt: '2026-11-05T12:00:00.000Z',
      },
    ];

    await writeStore(tasks);

    const storedTasks = await safeReadStore();
    assert.deepEqual(storedTasks, tasks);
  });
});
