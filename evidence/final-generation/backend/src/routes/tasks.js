import { Router } from 'express';
import { createTask, deleteTask, getTaskById, listTasks, updateStatus, updateTask } from '../services/taskService.js';

const router = Router();

router.get('/tasks', async (req, res, next) => {
  try {
    const tasks = await listTasks(req.query);
    res.status(200).json({ data: tasks });
  } catch (error) {
    next(error);
  }
});

router.get('/tasks/:id', async (req, res, next) => {
  try {
    const task = await getTaskById(req.params.id);
    res.status(200).json({ data: task });
  } catch (error) {
    next(error);
  }
});

router.post('/tasks', async (req, res, next) => {
  try {
    const task = await createTask(req.body);
    res.status(201).json({ data: task });
  } catch (error) {
    next(error);
  }
});

router.patch('/tasks/:id', async (req, res, next) => {
  try {
    const task = await updateTask(req.params.id, req.body);
    res.status(200).json({ data: task });
  } catch (error) {
    next(error);
  }
});

router.patch('/tasks/:id/status', async (req, res, next) => {
  try {
    const task = await updateStatus(req.params.id, req.body);
    res.status(200).json({ data: task });
  } catch (error) {
    next(error);
  }
});

router.delete('/tasks/:id', async (req, res, next) => {
  try {
    await deleteTask(req.params.id);
    res.status(204).send();
  } catch (error) {
    next(error);
  }
});

export default router;
