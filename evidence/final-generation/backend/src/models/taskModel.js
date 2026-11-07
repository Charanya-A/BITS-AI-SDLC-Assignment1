export const PRIORITY_LEVELS = ['HIGH', 'MEDIUM', 'LOW'];
export const STATUS_LEVELS = ['PENDING', 'IN_PROGRESS', 'COMPLETED'];

export const TASK_DEFAULTS = {
  priority: 'LOW',
  tags: [],
  status: 'PENDING',
};

export function createTaskRecord(payload = {}) {
  const now = new Date().toISOString();
  return {
    id: payload.id ?? '',
    title: payload.title ?? '',
    description: payload.description ?? '',
    priority: payload.priority ?? TASK_DEFAULTS.priority,
    tags: Array.isArray(payload.tags) ? payload.tags : [],
    status: payload.status ?? TASK_DEFAULTS.status,
    createdAt: payload.createdAt ?? now,
    updatedAt: payload.updatedAt ?? now,
  };
}
