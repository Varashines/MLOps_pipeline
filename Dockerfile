# --- STAGE 1: Builder ---
FROM python:3.13-slim AS builder

# Install uv (The fastest Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# --- STAGE 2: Runner ---
# This is the small, clean image with NO uv binary
FROM python:3.13-slim

WORKDIR /app

# Copy only the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy your application code
COPY . .

# Add the venv binaries to the PATH so 'dagster' is recognized directly
ENV PATH="/app/.venv/bin:$PATH"
ENV DAGSTER_HOME=/app

EXPOSE 3000

# Run using the python-managed binary directly
CMD ["dg", "dev", "-h", "0.0.0.0", "-p", "3000"]
