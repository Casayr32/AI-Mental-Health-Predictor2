module.exports = {
  apps: [
    {
      name: 'mindcare-ai-backend',
      script: './backend/server.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 5000,
        AI_SERVICE_URL: 'http://localhost:5001'
      }
    },
    {
      name: 'mindcare-ai-service',
      script: './ai-service/app.py',
      interpreter: 'python3',
      interpreter_args: '-u',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        PORT: 5001,
        MODEL_PATH: './model_artifacts/ai_model.joblib',
        DATASET_PATH: './dataset.csv'
      }
    }
  ]
};
