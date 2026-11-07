import test from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import fs from 'node:fs/promises';
import path from 'node:path';
import app from '../../src/app.js';
import { STORE_PATH } from '../../src/services/storageService.js';

async function resetStore() {
  await fs.mkdir(path.dirname(STORE_PATH), { recursive: true });
  await fs.writeFile(STORE_PATH, '[]', 'utf8');
}

test.beforeEach(async () => {
  await resetStore();
});

test('POST /api/tasks creates a task with generated UUID and timestamp metadata', async () => {
  const response = await request(app)
    .post('/api/tasks')
    .send({ title: 'Write report', description: 'Quarterly summary', priority: 'HIGH', tags: ['college', 'work'] });

  assert.equal(response.status, 201);
  assert.equal(response.body.data.title, 'Write report');
  assert.equal(response.body.data.priority, 'HIGH');
  assert.equal(response.body.data.status, 'PENDING');
  assert.match(response.body.data.id, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
  assert.ok(response.body.data.createdAt);
  assert.ok(response.body.data.updatedAt);
});

test('POST /api/tasks rejects invalid input without changing storage', async () => {
  const before = JSON.parse(await fs.readFile(STORE_PATH, 'utf8'));
  const response = await request(app)
    .post('/api/tasks')
    .send({ title: '', description: 'bad', priority: 'URGENT' });

  assert.equal(response.status, 400);
  assert.equal(response.body.error.code, 'VALIDATION_ERROR');

  const after = JSON.parse(await fs.readFile(STORE_PATH, 'utf8'));
  assert.deepEqual(after, before);
});

test('GET /api/tasks supports tag filtering and priority sorting', async () => {
  await request(app).post('/api/tasks').send({ title: 'Alpha', description: '', priority: 'LOW', tags: ['college'] });
  await request(app).post('/api/tasks').send({ title: 'Bravo', description: '', priority: 'HIGH', tags: ['college'] });
  await request(app).post('/api/tasks').send({ title: 'Charlie', description: '', priority: 'MEDIUM', tags: ['personal'] });

  const response = await request(app).get('/api/tasks?tag=college&sort=priority');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body.data.map((task) => task.title), ['Bravo', 'Alpha']);
});

test('PATCH /api/tasks/:id/status rejects invalid transitions without modifying stored task', async () => {
  const created = await request(app).post('/api/tasks').send({ title: 'Status task', description: '', priority: 'MEDIUM' });
  const before = JSON.parse(await fs.readFile(STORE_PATH, 'utf8'));

  const response = await request(app)
    .patch(`/api/tasks/${created.body.data.id}/status`)
    .send({ status: 'PENDING' });

  assert.equal(response.status, 409);
  assert.equal(response.body.error.code, 'INVALID_STATUS_TRANSITION');

  const after = JSON.parse(await fs.readFile(STORE_PATH, 'utf8'));
  assert.equal(after[0].status, before[0].status);
});
