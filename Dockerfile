# MindCare AI System - Production Dockerfile
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci && npm cache clean --force
COPY frontend/ ./
RUN npm run build

FROM node:20-alpine AS backend-build
WORKDIR /app/backend
COPY backend/package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY backend/ ./

FROM python:3.9-slim AS ai-service-build
WORKDIR /app/ai-service
COPY ai-service/requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages
COPY ai-service/*.py ./
COPY ai-service/dataset.csv ./
RUN python3 setup_model.py

FROM node:20-alpine
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
RUN mkdir -p /app/logs && chmod +x /app/backend/server.js
EXPOSE 5000 5001
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/test || exit 1
CMD ["sh", "-c", "pm2-runtime start ecosystem.config.js"]
