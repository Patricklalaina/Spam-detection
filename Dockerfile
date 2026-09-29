# --- Build : compile le site statique ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- Run : nginx sert le dossier dist (image finale ~50 Mo) ---
FROM nginx:1.27-alpine
# nginx remplace ${PORT} et ${API_UPSTREAM} au démarrage
ENV PORT=80
ENV API_UPSTREAM=http://backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
