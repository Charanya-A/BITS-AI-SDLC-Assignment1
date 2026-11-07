import app from './app.js';
import { initializeStore } from './services/storageService.js';

const port = Number(process.env.PORT || 3000);

initializeStore()
  .then(() => {
    app.listen(port, () => {
      console.log(`Smart Todo API listening on http://localhost:${port}`);
    });
  })
  .catch((error) => {
    console.error('Failed to initialize task store:', error.message || error);
    process.exit(1);
  });
