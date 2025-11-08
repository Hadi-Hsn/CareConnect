# Build stage
FROM node:20-alpine AS build

ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE:-http://localhost:8000/api/v1}

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application (Vite will pick up VITE_* env vars at build-time)
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
