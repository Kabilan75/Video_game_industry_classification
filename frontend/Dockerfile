# Base Stage
FROM node:18-alpine as base
WORKDIR /app
COPY package*.json ./
RUN npm install

# Development Stage
FROM base as dev
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]

# Build Stage
FROM base as build
COPY . .
ENV VITE_API_URL=""
RUN npm run build

# Production Stage
FROM nginx:alpine as prod
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
