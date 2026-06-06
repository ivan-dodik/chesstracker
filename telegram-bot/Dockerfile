FROM python:3.12-slim

# Install uv
RUN pip install uv --no-cache-dir

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY bot.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

# Run the bot
CMD ["uv", "run", "python", "bot.py"]