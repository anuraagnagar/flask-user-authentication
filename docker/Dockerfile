# Use a specific, secure Python base image
FROM python:3.11-alpine3.21

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 

# Set working directory in container
WORKDIR /app

# Install system dependencies (for psycopg2 and other C extensions)
RUN apk add --no-cache \
    bash \
    libpq \
    postgresql-dev \
    postgresql-client \
    netcat-openbsd


# Copy and install Python dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY ../ .

# Copy entrypoint.sh from docker/ into container and make it executable
COPY docker/docker-entrypoint.sh /app/docker/docker-entrypoint.sh
RUN chmod +x /app/docker/docker-entrypoint.sh

# Expose Flask default port
EXPOSE 5000

# Use the custom entrypoint script
ENTRYPOINT ["./app/docker/docker-entrypoint.sh"]
