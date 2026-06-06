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
COPY bot.py config.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

# Set ownership for the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Configure uv cache directory (writable by appuser)
ENV UV_CACHE_DIR=/home/appuser/.cache/uv

# Run the bot
CMD ["uv", "run", "python", "bot.py"]