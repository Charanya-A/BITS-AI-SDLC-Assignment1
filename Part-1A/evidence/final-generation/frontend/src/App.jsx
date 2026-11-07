import { useCallback, useEffect, useState } from 'react';
import { api } from './services/api.js';

const EMPTY_FORM = {
  title: '',
  description: '',
  priority: 'MEDIUM',
  tags: '',
  status: 'PENDING',
};

function App() {
  const [tasks, setTasks] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [filterTag, setFilterTag] = useState('');
  const [sortMode, setSortMode] = useState('priority');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const loadTasks = useCallback(async () => {
    try {
      const params = {};
      if (filterTag.trim()) params.tag = filterTag.trim();
      if (sortMode) params.sort = sortMode;
      const response = await api.getTasks(params);
      setTasks(response.data || []);
      setError('');
    } catch (err) {
      setError(err.message || 'Unable to load tasks.');
    }
  }, [filterTag, sortMode]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const resetForm = useCallback(() => {
    setForm(EMPTY_FORM);
    setEditingTaskId(null);
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const startEdit = (task) => {
    setEditingTaskId(task.id);
    setForm({
      title: task.title || '',
      description: task.description || '',
      priority: task.priority || 'MEDIUM',
      tags: (task.tags || []).join(', '),
      status: task.status || 'PENDING',
    });
    setError('');
    setSuccessMessage('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccessMessage('');

    try {
      const normalizedTags = form.tags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean);

      const patch = {
        title: form.title.trim(),
        description: form.description,
        priority: form.priority,
        tags: normalizedTags,
      };

      if (editingTaskId) {
        await api.updateTask(editingTaskId, patch);
        setSuccessMessage('Task updated successfully.');
      } else {
        await api.createTask({
          ...patch,
          status: form.status,
        });
        setSuccessMessage('Task created successfully.');
      }

      resetForm();
      await loadTasks();
    } catch (err) {
      const message = err.message || (editingTaskId ? 'Unable to update task.' : 'Unable to create task.');
      setError(message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this task?')) return;
    try {
      await api.deleteTask(id);
      await loadTasks();
      setSuccessMessage('Task deleted.');
    } catch (err) {
      setError(err.message || 'Unable to delete task.');
    }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await api.updateStatus(id, status);
      await loadTasks();
      setSuccessMessage('Status updated.');
    } catch (err) {
      setError(err.message || 'Unable to update status.');
    }
  };

  const cancelEdit = () => {
    resetForm();
    setError('');
    setSuccessMessage('');
  };

  return (
    <div className="app-shell">
      <header className="header">
        <div>
          <h1>Smart Todo & Task Manager</h1>
          <h2>{editingTaskId ? 'Edit task' : 'Create task'}</h2>
        </div>
      </header>

      <form className="task-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <label>
            Title
            <input name="title" value={form.title} onChange={handleChange} required />
          </label>
          <label>
            Priority
            <select name="priority" value={form.priority} onChange={handleChange}>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
            </select>
          </label>
          <label>
            Status
            <select name="status" value={form.status} onChange={handleChange}>
              <option value="PENDING">PENDING</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="COMPLETED">COMPLETED</option>
            </select>
          </label>
        </div>

        <label>
          Description
          <textarea name="description" value={form.description} onChange={handleChange} />
        </label>

        <label>
          Tags (comma separated)
          <input name="tags" value={form.tags} onChange={handleChange} />
        </label>

        <div className="controls">
          <button type="submit">{editingTaskId ? 'Save changes' : 'Create task'}</button>
          {editingTaskId && (
            <button type="button" className="secondary" onClick={cancelEdit}>
              Cancel
            </button>
          )}
        </div>

        {error && <div className="error">{error}</div>}
        {successMessage && <div className="success">{successMessage}</div>}
      </form>

      <div className="filter-row" style={{ marginTop: '18px' }}>
        <input
          aria-label="Filter by tag"
          placeholder="Filter by tag"
          value={filterTag}
          onChange={(event) => setFilterTag(event.target.value)}
        />
        <select value={sortMode} onChange={(event) => setSortMode(event.target.value)}>
          <option value="priority">Priority</option>
          <option value="">Default</option>
        </select>
      </div>

      <div className="task-grid">
        {tasks.length === 0 ? (
          <div className="empty-state">No tasks found.</div>
        ) : (
          tasks.map((task) => (
            <article key={task.id} className="task-card">
              <div className="task-meta">
                <strong>{task.title}</strong>
                <span className="status-badge">{task.status}</span>
                <span>{task.priority}</span>
              </div>
              <div>{task.description || 'No description.'}</div>
              <div className="tag-list">
                {(task.tags || []).map((tag) => (
                  <span key={`${task.id}-${tag}`} className="tag">#{tag}</span>
                ))}
              </div>
              <div className="controls">
                <button type="button" className="secondary" onClick={() => startEdit(task)}>
                  Edit
                </button>
                <button type="button" className="secondary" onClick={() => handleStatusChange(task.id, 'IN_PROGRESS')}>
                  Start
                </button>
                <button type="button" className="secondary" onClick={() => handleStatusChange(task.id, 'COMPLETED')}>
                  Complete
                </button>
                <button type="button" className="danger" onClick={() => handleDelete(task.id)}>
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
