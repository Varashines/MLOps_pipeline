# --- STAGE 1: Builder ---
FROM python:3.13-slim AS builder

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Optimization: Enable bytecode compilation for faster app startup
ENV UV_COMPILE_BYTECODE=1
# Optimization: Ensure uv copies files into the venv instead of symlinking
ENV UV_LINK_MODE=copy

WORKDIR /app

# 3. Optimization: Use BuildKit cache mounts to persist uv's cache between builds
# This means if you add ONE package, it doesn't re-download the others
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# --- STAGE 2: Runner ---
FROM python:3.13-slim

# 4. Security: Create a non-root user (Standard best practice)
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -d /app -s /bin/false appuser

WORKDIR /app

# Copy only the venv from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy code and set ownership
COPY --chown=appuser:appgroup . .

# Add this to your Stage 2
COPY dagster.yaml /app/dagster.yaml

# Environment setup
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
ENV DAGSTER_HOME=/app
ENV PYTHONUNBUFFERED=1

# 5. Security: Switch to the non-root user
USER appuser

EXPOSE 3000

CMD ["dg", "dev", "-h", "0.0.0.0", "-p", "3000"]
