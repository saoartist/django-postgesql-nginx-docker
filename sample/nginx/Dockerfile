# =============================================================================
# Nginx Dockerfile
# =============================================================================
# Uses the official Nginx Alpine image (very small ~5MB)
# and replaces the default config with our custom one.
# =============================================================================

FROM nginx:1.27-alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config
COPY nginx.conf /etc/nginx/conf.d/
