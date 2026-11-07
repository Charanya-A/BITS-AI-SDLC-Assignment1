import { PRIORITY_LEVELS } from '../models/taskModel.js';

export function sortTasks(tasks, { sort = null } = {}) {
  const safeTasks = [...tasks];
  if (sort !== 'priority') return safeTasks;

  return safeTasks.sort((a, b) => {
    const aPriority = PRIORITY_LEVELS.indexOf(a.priority);
    const bPriority = PRIORITY_LEVELS.indexOf(b.priority);

    if (aPriority !== bPriority) {
      return aPriority - bPriority;
    }

    const aTime = new Date(a.createdAt).getTime();
    const bTime = new Date(b.createdAt).getTime();
    if (aTime !== bTime) return aTime - bTime;

    return String(a.id).localeCompare(String(b.id));
  });
}
