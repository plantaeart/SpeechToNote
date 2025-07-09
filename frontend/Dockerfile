FROM node:22.16.0 as build-stage
WORKDIR /app/speech-to-note-frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=build-stage /app/speech-to-note-frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]