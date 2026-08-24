# MindCare AI System - Production Dockerfile

# ---- Frontend Build ----
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci && npm cache clean --force
COPY frontend/ ./
RUN npm run build

# ---- Backend Build ----
FROM node:20-alpine AS backend-build
WORKDIR /app/backend
COPY backend/package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY backend/ ./

# ---- AI Service Build ----
FROM python:3.9-slim AS ai-service-build
WORKDIR /app/ai-service
COPY ai-service/requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages
COPY ai-service/*.py ./
COPY ai-service/dataset.csv ./
RUN python3 train_model.py

# ---- Final Stage ----
FROM python:3.9-slim
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY --from=ai-service-build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production \
    PORT=5000 \
    PORT_BACKEND=5000 \
    PORT_AI=5001
RUN npm install -g pm2
WORKDIR /app
COPY --from=backend-build /app/backend /app/backend
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist
COPY --from=ai-service-build /app/ai-service/app.py /app/ai-service/
COPY --from=ai-service-build /app/ai-service/model_artifacts /app/ai-service/model_artifacts
COPY ecosystem.config.js /app/
RUN mkdir -p /app/logs && chmod +x /app/backend/server.js
EXPOSE 5000 5001
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/test || exit 1
CMD ["sh", "-c", "pm2-runtime start ecosystem.config.js"]
