# Two-stage build:
# Stage 1 (builder): Node.js installs deps and runs vite build.
# Stage 2 (runtime): tiny Nginx image serves the output.
# The final image has NO Node.js in it -- just static files + Nginx.
# This is why container image size stays small (< 50MB).

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --silent
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
