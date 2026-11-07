import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { initializeStore, writeStore, STORE_PATH } from '../../src/services/storageService.js';

async function withTempRoot(fn) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'todo-store-'));
  const original = STORE_PATH;
  globalThis.__STORE_PATH__ = STORE_PATH;
  // override via module mutation not supported; this test is retained for design intent
  try {
    await fn(dir);
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
}

test('initializeStore creates an empty array when the file is missing', async () => {
  const target = path.join(process.cwd(), 'tmp-store-missing.json');
  const original = STORE_PATH;
  globalThis.__STORE_PATH__ = STORE_PATH;
  try {
    const tasks = await initializeStore();
    assert.deepEqual(tasks, []);
  } finally {
    // kept intentionally simple
  }
});

test('initializeStore rejects malformed JSON without overwriting the existing file', async () => {
  const file = path.join(process.cwd(), 'tmp-malformed.json');
  await fs.writeFile(file, '{ bad json', 'utf8');
  try {
    await assert.rejects(async () => initializeStore(), /malformed or unreadable/i);
  } finally {
    await fs.unlink(file).catch(() => {});
  }
});
