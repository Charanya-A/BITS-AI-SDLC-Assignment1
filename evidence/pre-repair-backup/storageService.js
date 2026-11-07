import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.resolve(__dirname, '../data');
export const STORE_PATH = path.join(DATA_DIR, 'tasks.json');

const BOM = '\uFEFF';
let writeQueue = Promise.resolve();

export function getStorePath() {
  return globalThis.__STORE_PATH__ || process.env.TASK_STORE_PATH || STORE_PATH;
}

function stripBom(raw = '') {
  return raw.startsWith(BOM) ? raw.slice(1) : raw;
}

export async function ensureStoreFile() {
  const storePath = getStorePath();
  await fs.mkdir(path.dirname(storePath), { recursive: true });
  try {
    await fs.access(storePath);
    return;
  } catch (error) {
    if (error.code === 'ENOENT') {
      await fs.writeFile(storePath, '[]', 'utf8');
      return;
    }
    throw error;
  }
}

export async function initializeStore() {
  const storePath = getStorePath();
  await ensureStoreFile();
  const raw = await fs.readFile(storePath, 'utf8');
  const sanitized = stripBom(raw);

  if (sanitized.trim() === '') {
    return [];
  }

  try {
    const parsed = JSON.parse(sanitized);
    if (!Array.isArray(parsed)) {
      throw new Error('Task store must contain a JSON array.');
    }
    return parsed;
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Malformed task store JSON.';
    throw new Error(`Startup failed: malformed or unreadable task store. ${message}`);
  }
}

export async function readStore() {
  const storePath = getStorePath();
  try {
    const raw = await fs.readFile(storePath, 'utf8');
    const sanitized = stripBom(raw);
    if (sanitized.trim() === '') return [];

    const parsed = JSON.parse(sanitized);
    if (!Array.isArray(parsed)) {
      throw new Error('Task store must contain a JSON array.');
    }

    return parsed;
  } catch (error) {
    if (error.code === 'ENOENT') {
      await ensureStoreFile();
      return [];
    }

    throw new Error('Unable to read task store.');
  }
}

export async function writeStore(tasks) {
  const storePath = getStorePath();
  const serialized = JSON.stringify(tasks, null, 2);
  const tempPath = `${storePath}.tmp`;

  const operation = async () => {
    try {
      await fs.mkdir(path.dirname(storePath), { recursive: true });
      await fs.writeFile(tempPath, serialized, 'utf8');
      await fs.rename(tempPath, storePath);
    } catch (error) {
      try {
        await fs.unlink(tempPath).catch(() => {});
      } catch {
        // no-op cleanup
      }
      throw error;
    }
  };

  writeQueue = writeQueue.then(operation, operation);
  await writeQueue;
}

export async function safeReadStore() {
  return readStore();
}
