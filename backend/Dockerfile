FROM python:3.13.3

# Set working directory to your FastAPI backend
WORKDIR /app/speech-to-note-backend

# Copy only what's needed to create the environment first
COPY speech-to-note-backend/pyproject.toml .

# Install uv globally for the build steps
RUN pip install uv

# Create virtualenv and install dependencies inside correct dir
RUN uv venv
RUN uv pip install -r pyproject.toml
RUN uv pip install uvicorn

# Now copy your full source into the container
COPY speech-to-note-backend/app app

# Environment and port
ENV CONFIG_ENV=config_local_docker_env
EXPOSE 8000

# Run FastAPI app using uv
CMD ["uv", "run","uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
