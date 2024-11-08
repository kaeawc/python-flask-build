# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Change default shell from /bin/ash to /bin/bash
SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

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

RUN source ./.venv/bin/activate

# Run the app, pass both the port and debug flag as arguments
CMD ["python", "src/main.py", "$PORT", "$DEBUG"]
