# Multi-stage build for webapp
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy source files
COPY index.html style.css script.js config.js ./

# Production stage with nginx
FROM nginx:alpine

# Install envsubst for environment variable substitution
RUN apk add --no-cache gettext

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy webapp files
COPY --from=builder /app/ /usr/share/nginx/html/

# Set default environment variables
ENV API_BASE_URL=http://localhost:5001/api/v1

# Create entrypoint script to substitute environment variables
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-inject-env.sh && \
    echo 'envsubst < /usr/share/nginx/html/config.js > /tmp/config.js && mv /tmp/config.js /usr/share/nginx/html/config.js' >> /docker-entrypoint.d/40-inject-env.sh && \
    chmod +x /docker-entrypoint.d/40-inject-env.sh

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]