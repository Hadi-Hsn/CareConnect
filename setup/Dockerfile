FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/setup

# Copy backend requirements for database access
COPY backend/pyproject.toml /app/backend/pyproject.toml

# Install Python dependencies
RUN cd /app/backend && \
    pip install --no-cache-dir -e .

# Copy setup scripts
COPY setup/scripts /app/setup/scripts
COPY setup/run_setup.sh /app/setup/run_setup.sh

# Copy backend app for imports
COPY backend/app /app/backend/app
COPY backend/alembic /app/backend/alembic
COPY backend/alembic.ini /app/backend/alembic.ini

# Make setup script executable
RUN chmod +x /app/setup/run_setup.sh

# Create data directories
RUN mkdir -p /app/data/doctor_pdfs /app/data/vectorstore

CMD ["/app/setup/run_setup.sh"]
