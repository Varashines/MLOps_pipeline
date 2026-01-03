# ==========================================
# STAGE 1: The Builder (Compiles the Environment)
# ==========================================
FROM python:3.13-slim AS builder

# 1. Install uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 2. Copy ONLY dependency files first
# This is crucial for Docker caching. If pyproject.toml doesn't change,
# Docker skips the "uv sync" step on re-builds.
COPY pyproject.toml uv.lock ./

# 3. Install dependencies into .venv
# --frozen: Fails if lockfile is out of date (Safety)
# --no-install-project: Installs libs but skips installing 'your' code package
RUN uv sync --frozen --no-install-project

# ==========================================
# STAGE 2: The Runner (Execution)
# ==========================================
FROM python:3.13-slim

WORKDIR /app

# 1. Copy the Virtual Environment from builder
COPY --from=builder /app/.venv /app/.venv

# 2. Add venv to PATH
# Now 'python' and 'dagster' commands work automatically
ENV PATH="/app/.venv/bin:$PATH"

# 3. Copy your actual code
# We do this LAST so code changes don't invalidate the cache
COPY . .

# 4. Run Dagster
# We point to the specific file you are working on
ENV DAGSTER_HOME=/app
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-f", "dagsterBasics/session2.py"]
