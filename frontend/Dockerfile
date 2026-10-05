# Build context is this directory (frontend/), see infra/docker-compose.yml.
FROM node:22.16.0 AS build-stage
WORKDIR /app
# The Vue app lives in the subfolder; this directory also holds the entrypoint.
COPY speech-to-note-frontend ./
# Select which src/config/env.local*.ts to build against
ARG VITE_CONFIG_ENV_FRONT=local_docker
ENV VITE_CONFIG_ENV_FRONT=${VITE_CONFIG_ENV_FRONT}
# Reproducible install: package-lock.json is committed
RUN npm ci
RUN npm run build

FROM nginx:alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Runtime config: writes env.js from environment variables on start,
# so the Google API key is never baked into an image layer.
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 80
ENTRYPOINT ["/docker-entrypoint.sh"]