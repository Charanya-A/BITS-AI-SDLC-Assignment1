import { randomUUID } from 'node:crypto';
import { createTaskRecord } from '../models/taskModel.js';
import { readStore, writeStore } from './storageService.js';
import {
  validateCreateTaskInput,
  validateUpdateTaskInput,
  validateStatusBody,
  validateStatusTransition,
} from './validationService.js';
import { makeInvalidStatusTransitionError, makeNotFoundError, makePersistenceError } from '../utils/errors.js';
import { sortTasks } from '../utils/sort.js';

export async function listTasks(query = {}) {
  try {
    const tasks = await readStore();
    const tag = query.tag ? String(query.tag).trim().toLowerCase() : null;
    const filtered = tag
      ? tasks.filter((task) => (task.tags || []).some((item) => String(item).trim().toLowerCase() === tag))
      : tasks;
    return sortTasks(filtered, { sort: query.sort });
  } catch (error) {
    throw Object.assign(new Error('Unable to read tasks.'), { code: 'PERSISTENCE_ERROR' });
  }
}

export async function getTaskById(id) {
  try {
    const tasks = await readStore();
    const task = tasks.find((candidate) => candidate.id === id);
    if (!task) throw makeNotFoundError(`Task with id ${id} was not found.`);
    return task;
  } catch (error) {
    if (error && error.error && error.error.code === 'NOT_FOUND') throw error;
    throw Object.assign(new Error('Unable to read task.'), { code: 'PERSISTENCE_ERROR' });
  }
}

export async function createTask(input) {
  try {
    const validated = validateCreateTaskInput(input);
    const tasks = await readStore();
    const now = new Date().toISOString();
    const task = {
      ...createTaskRecord({
        ...validated,
        id: randomUUID(),
        createdAt: now,
        updatedAt: now,
      }),
      tags: validated.tags || [],
      status: validated.status || 'PENDING',
    };

    tasks.push(task);
    await writeStore(tasks);
    return task;
  } catch (error) {
    if (error && error.code === 'VALIDATION_ERROR') throw error;
    if (error && error.error && error.error.code === 'NOT_FOUND') throw error;
    if (error && error.code === 'PERSISTENCE_ERROR') throw error;
    if (error && error.message) {
      const validationError = new Error(error.message);
      validationError.code = 'VALIDATION_ERROR';
      throw validationError;
    }
    throw Object.assign(new Error('Unable to create task.'), { code: 'PERSISTENCE_ERROR' });
  }
}

export async function updateTask(id, input) {
  try {
    const tasks = await readStore();
    const index = tasks.findIndex((task) => task.id === id);
    if (index === -1) throw makeNotFoundError(`Task with id ${id} was not found.`);

    const base = { ...tasks[index] };
    const sanitized = validateUpdateTaskInput(input);

    const merged = {
      ...base,
      ...sanitized,
      updatedAt: new Date().toISOString(),
};

    tasks[index] = merged;
    await writeStore(tasks);
    return merged;
  } catch (error) {
    if (error && error.error && error.error.code === 'NOT_FOUND') throw error;
    if (error && error.code === 'VALIDATION_ERROR') throw error;
    if (error && error.code === 'PERSISTENCE_ERROR') throw error;
    throw makePersistenceError('Unable to update task.');
  }
}

export async function updateStatus(id, input) {
  try {
    const tasks = await readStore();
    const taskIndex = tasks.findIndex((task) => task.id === id);
    if (taskIndex === -1) throw makeNotFoundError(`Task with id ${id} was not found.`);

    const payload = validateStatusBody(input);
    validateStatusTransition(tasks[taskIndex].status, payload.status);

    tasks[taskIndex] = {
      ...tasks[taskIndex],
      status: payload.status,
      updatedAt: new Date().toISOString(),
    };

    await writeStore(tasks);
    return tasks[taskIndex];
  } catch (error) {
    if (error && error.error && error.error.code === 'NOT_FOUND') throw error;
    if (error && error.code === 'INVALID_STATUS_TRANSITION') throw makeInvalidStatusTransitionError(error.message);
    if (error && error.code === 'VALIDATION_ERROR') throw error;
    if (error && error.code === 'PERSISTENCE_ERROR') throw error;
    throw makePersistenceError('Unable to update task status.');
  }
}

export async function deleteTask(id) {
  try {
    const tasks = await readStore();
    const index = tasks.findIndex((task) => task.id === id);
    if (index === -1) throw makeNotFoundError(`Task with id ${id} was not found.`);

    tasks.splice(index, 1);
    await writeStore(tasks);
    return true;
  } catch (error) {
    if (error && error.error && error.error.code === 'NOT_FOUND') throw error;
    throw makePersistenceError('Unable to delete task.');
  }
}
