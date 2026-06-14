FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies (with BuildKit cache mount for uv)
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# Copy application code
COPY bot.py config.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

# Set ownership for the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run the bot
CMD [".venv/bin/python", "bot.py"]
