
import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import app from '../../src/app.js';

let temporaryDirectory;
let testStorePath;
let previousStorePath;

async function resetStore() {
  await fs.writeFile(testStorePath, '[]', 'utf8');
}

test.before(async () => {
  temporaryDirectory = await fs.mkdtemp(
    path.join(os.tmpdir(), 'todo-api-')
  );

  testStorePath = path.join(temporaryDirectory, 'tasks.json');
  previousStorePath = globalThis.__STORE_PATH__;

  globalThis.__STORE_PATH__ = testStorePath;

  await resetStore();
});

test.beforeEach(async () => {
  await resetStore();
});

test.after(async () => {
  if (previousStorePath === undefined) {
    delete globalThis.__STORE_PATH__;
  } else {
    globalThis.__STORE_PATH__ = previousStorePath;
  }

  await fs.rm(temporaryDirectory, { recursive: true, force: true });
});

test('POST /api/tasks creates a task with generated UUID and timestamp metadata', async () => {
  const response = await request(app)
    .post('/api/tasks')
    .send({
      title: 'Write report',
      description: 'Quarterly summary',
      priority: 'HIGH',
      tags: ['college', 'work'],
    });

  assert.equal(response.status, 201);
  assert.equal(response.body.data.title, 'Write report');
  assert.equal(response.body.data.priority, 'HIGH');
  assert.equal(response.body.data.status, 'PENDING');

  assert.match(
    response.body.data.id,
    /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  );

  assert.ok(response.body.data.createdAt);
  assert.ok(response.body.data.updatedAt);
});

test('POST /api/tasks rejects invalid input without changing storage', async () => {
  const before = JSON.parse(await fs.readFile(testStorePath, 'utf8'));

  const response = await request(app)
    .post('/api/tasks')
    .send({
      title: '',
      description: 'bad',
      priority: 'URGENT',
    });

  assert.equal(response.status, 400);
  assert.equal(response.body.error.code, 'VALIDATION_ERROR');

  const after = JSON.parse(await fs.readFile(testStorePath, 'utf8'));
  assert.deepEqual(after, before);
});

test('GET /api/tasks supports tag filtering and priority sorting', async () => {
  await request(app)
    .post('/api/tasks')
    .send({ title: 'Alpha', description: '', priority: 'LOW', tags: ['college'] });

  await request(app)
    .post('/api/tasks')
    .send({ title: 'Bravo', description: '', priority: 'HIGH', tags: ['college'] });

  await request(app)
    .post('/api/tasks')
    .send({ title: 'Charlie', description: '', priority: 'MEDIUM', tags: ['personal'] });

  const response = await request(app)
    .get('/api/tasks?tag=college&sort=priority');

  assert.equal(response.status, 200);
  assert.deepEqual(
    response.body.data.map((task) => task.title),
    ['Bravo', 'Alpha']
  );
});
test('PATCH /api/tasks/:id updates allowed fields and preserves immutable metadata', async () => {
  const created = await request(app)
    .post('/api/tasks')
    .send({
      title: 'Original title',
      description: 'Original description',
      priority: 'LOW',
      tags: ['college'],
    });

  assert.equal(created.status, 201);

  const originalTask = created.body.data;

  // Ensure updatedAt can be distinguished from createdAt.
  await new Promise((resolve) => setTimeout(resolve, 10));

  const response = await request(app)
    .patch(`/api/tasks/${originalTask.id}`)
    .send({
      title: 'Updated title',
      description: 'Updated description',
      priority: 'HIGH',
      tags: ['college', 'updated'],
    });

  assert.equal(response.status, 200);
  assert.equal(response.body.data.id, originalTask.id);
  assert.equal(response.body.data.title, 'Updated title');
  assert.equal(response.body.data.description, 'Updated description');
  assert.equal(response.body.data.priority, 'HIGH');
  assert.deepEqual(response.body.data.tags, ['college', 'updated']);
  assert.equal(response.body.data.status, 'PENDING');
  assert.equal(response.body.data.createdAt, originalTask.createdAt);
  assert.notEqual(response.body.data.updatedAt, originalTask.updatedAt);

  const storedTasks = JSON.parse(
    await fs.readFile(testStorePath, 'utf8')
  );

  assert.deepEqual(storedTasks[0], response.body.data);
});

test('PATCH /api/tasks/:id rejects immutable fields without changing storage', async () => {
  const created = await request(app)
    .post('/api/tasks')
    .send({
      title: 'Protected task',
      description: '',
      priority: 'MEDIUM',
    });

  const originalTask = created.body.data;
  const before = JSON.parse(await fs.readFile(testStorePath, 'utf8'));

  const response = await request(app)
    .patch(`/api/tasks/${originalTask.id}`)
    .send({
      title: 'Attempted change',
      status: 'COMPLETED',
    });

  assert.equal(response.status, 400);
  assert.equal(response.body.error.code, 'VALIDATION_ERROR');

  const after = JSON.parse(await fs.readFile(testStorePath, 'utf8'));
  assert.deepEqual(after, before);
});

test('PATCH /api/tasks/:id/status rejects invalid transitions without modifying stored task', async () => {
  const created = await request(app)
    .post('/api/tasks')
    .send({
      title: 'Status task',
      description: '',
      priority: 'MEDIUM',
    });

  const before = JSON.parse(await fs.readFile(testStorePath, 'utf8'));

  const response = await request(app)
    .patch(`/api/tasks/${created.body.data.id}/status`)
    .send({ status: 'PENDING' });

  assert.equal(response.status, 409);
  assert.equal(response.body.error.code, 'INVALID_STATUS_TRANSITION');

  const after = JSON.parse(await fs.readFile(testStorePath, 'utf8'));
  assert.equal(after[0].status, before[0].status);
});
