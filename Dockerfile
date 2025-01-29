# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FASTAPI_PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the port for FastAPI
EXPOSE ${FASTAPI_PORT}

# Command to run the FastAPI application
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${FASTAPI_PORT} "]
