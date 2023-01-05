ARG FRAPPE_DOCKER_VERSION=v14
ARG FRAPPE_GIT_VERSION=version-14
ARG ERPNEXT_VERSION=version-14

# Prepare builder image
FROM frappe/bench:latest as assets

ARG APP_NAME

# Setup frappe-bench using FRAPPE_VERSION
RUN bench init --version=${FRAPPE_GIT_VERSION} --skip-redis-config-generation --verbose --skip-assets /home/frappe/frappe-bench
WORKDIR /home/frappe/frappe-bench

# Comment following if ERPNext is not required
RUN bench get-app --branch=${ERPNEXT_VERSION} --skip-assets --resolve-deps erpnext

# Copy custom app(s)
COPY --chown=frappe:frappe . apps/${APP_NAME}

# Setup dependencies
RUN bench setup requirements

# Build static assets, copy files instead of symlink
RUN bench build --production --verbose --hard-link


# Use frappe-nginx image with nginx template and env vars
FROM frappe/frappe-nginx:${FRAPPE_DOCKER_VERSION}

# Remove existing assets
USER root
RUN rm -fr /usr/share/nginx/html/assets

# Copy built assets
COPY --from=assets /home/frappe/frappe-bench/sites/assets /usr/share/nginx/html/assets

# Use non-root user
USER 1000
