FROM node:22.16.0 AS build-stage
WORKDIR /app
COPY /speech-to-note-frontend ./
RUN npm install
RUN npm run build
FROM nginx:alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]