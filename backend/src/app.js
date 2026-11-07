import express from 'express';
import cors from 'cors';
import taskRoutes from './routes/tasks.js';
import { makeMalformedRequestError, makeNotFoundError, makePersistenceError } from './utils/errors.js';

const app = express();

app.use(cors());
app.use(express.json({ strict: true }));
app.use('/api', taskRoutes);

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json(makeMalformedRequestError('Malformed JSON request body.'));
  }

  if (err && err.code === 'VALIDATION_ERROR') {
    return res.status(400).json({ error: { code: 'VALIDATION_ERROR', message: err.message } });
  }

  if (err && err.code === 'MALFORMED_REQUEST') {
    return res.status(400).json({ error: { code: 'MALFORMED_REQUEST', message: err.message } });
  }

  if (err && err.code === 'NOT_FOUND') {
    return res.status(404).json({ error: { code: 'NOT_FOUND', message: err.message } });
  }

  if (err && err.code === 'INVALID_STATUS_TRANSITION') {
    return res.status(409).json({ error: { code: 'INVALID_STATUS_TRANSITION', message: err.message } });
  }

  if (err && err.code === 'PERSISTENCE_ERROR') {
    return res.status(500).json(makePersistenceError('A persistence error occurred while processing the request.'));
  }

  console.error('Unhandled error:', err);
  return res.status(500).json(makePersistenceError('An unexpected server error occurred.'));
});

app.use((req, res) => {
  res.status(404).json(makeNotFoundError('Route not found.'));
});

export default app;
