# Multi-stage build for React frontend
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1001 -S rhiz && \
    adduser -S rhiz -u 1001

# Set ownership
RUN chown -R rhiz:rhiz /usr/share/nginx/html && \
    chown -R rhiz:rhiz /var/cache/nginx && \
    chown -R rhiz:rhiz /var/log/nginx && \
    chown -R rhiz:rhiz /etc/nginx/conf.d

# Switch to non-root user
USER rhiz

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]