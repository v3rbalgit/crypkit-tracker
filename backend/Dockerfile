# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Everything outputs to the terminal (no buffering)
ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# Set up app directory
WORKDIR /app

# Copy dependency specification
COPY pyproject.toml .

# Install uv and dependencies in a single RUN step
RUN uv pip compile pyproject.toml > requirements.txt && \
    uv pip install --system -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure logs directory exists
RUN mkdir -p /app/logs

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos "" app && \
    chown -R app:app /app
USER app

# Expose the port that the application runs on
EXPOSE 8000
