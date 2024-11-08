# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container (if needed)
EXPOSE 80

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default port and debug flag for development
ARG PORT=5000
ARG DEBUG=false
ENV PORT=${PORT}
ENV DEBUG=${DEBUG}

RUN source ./.venv/bin/activate

# Run the app, pass both the port and debug flag as arguments
CMD ["python", "src/main.py", "$PORT", "$DEBUG"]
