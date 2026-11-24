# Use an official Python runtime as a parent image, matching .python-version
FROM python:3.11-slim

# Install a pinned uv, see https://docs.astral.sh/uv/guides/integration/docker/
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Compile bytecode for faster startup, use the image's Python, and keep no uv cache in the image
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_NO_CACHE=1

# Install dependencies in their own layer so it is reused when only the source changes
COPY pyproject.toml uv.lock /app/
RUN uv sync --locked --no-install-project

# Copy the current directory contents into the container at /app
COPY . /app
RUN uv sync --locked

# Use the project environment
ENV PATH="/app/.venv/bin:$PATH"

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default port and debug flag for development
ARG PORT=5000
ARG DEBUG=false
ENV PORT=${PORT}
ENV DEBUG=${DEBUG}

# Make port available to the world outside this container (if needed)
EXPOSE ${PORT}

# Run the app, which reads the port and debug flag from PORT and DEBUG
CMD ["python", "src/main.py"]
