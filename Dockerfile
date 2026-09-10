# Explicit base image version — never use :latest in production Dockerfiles
FROM python:3.12-slim

# Application metadata (OCI labels filled at build time via --build-arg)
ARG APP_VERSION=0.0.0
ARG GIT_COMMIT=unknown
ARG GIT_REPOSITORY=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="student-ml-api" \
      org.opencontainers.image.description="ML inference prediction API" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.source="${GIT_REPOSITORY}" \
      org.opencontainers.image.created="${BUILD_DATE}"

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source after dependencies
COPY app.py .
COPY VERSION .

EXPOSE 5000

# Use gunicorn for a production-oriented process model
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
