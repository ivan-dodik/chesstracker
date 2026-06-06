FROM python:3.12-slim

# Install uv
RUN pip install uv --no-cache-dir

# Set working directory
WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Set ownership for the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Configure uv cache directory (writable by appuser)
ENV UV_CACHE_DIR=/home/appuser/.cache/uv

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]