FROM python:3.13.3 AS dependencies-stage
# Get uv from the official image
COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /bin/

# Set working directory to your FastAPI backend
WORKDIR /app

# Now copy your full source into the container
COPY . /app

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

FROM python:3.13.3-slim AS production-stage
# Get uv from the official image
COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy the virtual environment from the dependencies stage
COPY --from=dependencies-stage /app/.venv /app/.venv

# Copy your application code
COPY --from=dependencies-stage /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Environment and port
ENV CURRENT_ENV=docker
EXPOSE 8000

# Run FastAPI app using uv
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]
