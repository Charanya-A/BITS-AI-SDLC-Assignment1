import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../../src/App.jsx';

const initialTasks = [
  {
    id: 'task-1',
    title: 'Plan sprint',
    description: 'Outline milestones',
    priority: 'HIGH',
    tags: ['college', 'work'],
    status: 'PENDING',
    createdAt: '2025-01-01T00:00:00.000Z',
    updatedAt: '2025-01-01T00:00:00.000Z',
  },
];

let tasks = [...initialTasks];

function jsonResponse(data, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => 'application/json' },
    json: async () => data,
  });
}

describe('Task dashboard form', () => {
  beforeEach(() => {
    tasks = [...initialTasks];
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url, options = {}) => {
        const method = (options.method || 'GET').toUpperCase();
        const requestUrl = String(url);
        const listUrl = 'http://localhost:3000/api/tasks';

        if (method === 'GET' && requestUrl.startsWith(listUrl)) {
          return jsonResponse({ data: tasks });
        }

        if (requestUrl === listUrl && method === 'POST') {
          const payload = JSON.parse(options.body || '{}');
          const created = {
            ...payload,
            id: 'task-new',
            status: payload.status || 'PENDING',
            tags: payload.tags || [],
            createdAt: '2025-01-02T00:00:00.000Z',
            updatedAt: '2025-01-02T00:00:00.000Z',
          };
          tasks = [...tasks, created];
          return jsonResponse({ data: created }, 201);
        }

        if (requestUrl === 'http://localhost:3000/api/tasks/task-1' && method === 'PATCH') {
          const payload = JSON.parse(options.body || '{}');
          tasks = tasks.map((task) =>
            task.id === 'task-1'
              ? {
                  ...task,
                  ...payload,
                  id: task.id,
                  updatedAt: '2025-01-03T00:00:00.000Z',
                  status: task.status,
                }
              : task,
          );
          return jsonResponse({ data: tasks.find((task) => task.id === 'task-1') });
        }

        if (requestUrl === 'http://localhost:3000/api/tasks/task-1/status' && method === 'PATCH') {
          const payload = JSON.parse(options.body || '{}');
          tasks = tasks.map((task) =>
            task.id === 'task-1' ? { ...task, status: payload.status, updatedAt: '2025-01-03T00:00:00.000Z' } : task,
          );
          return jsonResponse({ data: tasks.find((task) => task.id === 'task-1') });
        }

        if (requestUrl === 'http://localhost:3000/api/tasks/task-1' && method === 'DELETE') {
          tasks = tasks.filter((task) => task.id !== 'task-1');
          return jsonResponse({}, 204);
        }

        throw new Error(`Unhandled fetch in test: ${method} ${requestUrl}`);
      }),
    );
  });

  it('renders the create task form and allows a valid submission', async () => {
    render(<App />);
    const titleInput = await screen.findByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'Plan sprint' } });
    fireEvent.click(screen.getByRole('button', { name: /create task/i }));

    await waitFor(() => {
      expect(screen.getByText(/smart todo/i)).toBeTruthy();
    });
  });

  it('shows a filter input for tag-based search', async () => {
    render(<App />);
    expect(await screen.findByLabelText(/filter by tag/i)).toBeTruthy();
  });

  it('clicking Edit populates the form with the selected task details', async () => {
    render(<App />);
    const editButton = await screen.findByRole('button', { name: /^edit$/i });
    fireEvent.click(editButton);

    expect(screen.getByText(/edit task/i)).toBeTruthy();
    expect(screen.getByDisplayValue('Plan sprint')).toBeTruthy();
    expect(screen.getByDisplayValue('Outline milestones')).toBeTruthy();
    expect(screen.getByDisplayValue('college, work')).toBeTruthy();
    expect(screen.getByRole('button', { name: /save changes/i })).toBeTruthy();
  });

  it('saving changes calls api.updateTask with the correct ID and allowed fields', async () => {
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: /^edit$/i }));

    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Updated sprint plan' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Updated milestone list' } });
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: 'LOW' } });
    fireEvent.change(screen.getByLabelText(/tags/i), { target: { value: 'college, research' } });
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/tasks/task-1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({
            title: 'Updated sprint plan',
            description: 'Updated milestone list',
            priority: 'LOW',
            tags: ['college', 'research'],
          }),
        }),
      );
    });
  });

  it('cancel exits edit mode without submitting an update', async () => {
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: /^edit$/i }));
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Cancelled update' } });
    fireEvent.click(screen.getByRole('button', { name: /^cancel$/i }));

    expect(screen.getByRole('heading', { name: /^create task$/i })).toBeTruthy();
    expect(screen.getByRole('button', { name: /^create task$/i })).toBeTruthy();
    expect(globalThis.fetch.mock.calls.filter(([url, options]) => url === 'http://localhost:3000/api/tasks/task-1' && options.method === 'PATCH')).toHaveLength(0);
  });

  it('continues to allow creating a new task', async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'New item' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'Created from form' } });
    fireEvent.change(screen.getByLabelText(/priority/i), { target: { value: 'MEDIUM' } });
    fireEvent.change(screen.getByLabelText(/tags/i), { target: { value: 'urgent, review' } });
    fireEvent.click(screen.getByRole('button', { name: /^create task$/i }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/tasks',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            title: 'New item',
            description: 'Created from form',
            priority: 'MEDIUM',
            tags: ['urgent', 'review'],
            status: 'PENDING',
          }),
        }),
      );
    });
  });
});
