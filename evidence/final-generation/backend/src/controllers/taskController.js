import { createTask, deleteTask, getTaskById, listTasks, updateStatus, updateTask } from '../services/taskService.js';

export async function getTasksController(req, res, next) {
  try {
    const tasks = await listTasks(req.query);
    res.status(200).json({ data: tasks });
  } catch (error) {
    next(error);
  }
}

export async function getTaskByIdController(req, res, next) {
  try {
    const task = await getTaskById(req.params.id);
    res.status(200).json({ data: task });
  } catch (error) {
    next(error);
  }
}

export async function createTaskController(req, res, next) {
  try {
    const task = await createTask(req.body);
    res.status(201).json({ data: task });
  } catch (error) {
    next(error);
  }
}

export async function updateTaskController(req, res, next) {
  try {
    const task = await updateTask(req.params.id, req.body);
    res.status(200).json({ data: task });
  } catch (error) {
    next(error);
  }
}

export async function updateTaskStatusController(req, res, next) {
  try {
    const task = await updateStatus(req.params.id, req.body);
    res.status(200).json({ data: task });
  } catch (error) {
    next(error);
  }
}

export async function deleteTaskController(req, res, next) {
  try {
    await deleteTask(req.params.id);
    res.status(204).send();
  } catch (error) {
    next(error);
  }
}
