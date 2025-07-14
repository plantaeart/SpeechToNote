FROM node:22.16.0 AS build-stage
WORKDIR /app
COPY /speech-to-note-frontend ./
# Accept build argument and set as environment variable for build
ARG VITE_CONFIG_ENV_FRONT=local_docker
ENV VITE_CONFIG_ENV_FRONT=${VITE_CONFIG_ENV_FRONT}
RUN npm install
RUN npm run build
FROM nginx:alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]