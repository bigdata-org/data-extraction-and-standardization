# Use an ARM-compatible Python 3.12 image
FROM --platform=linux/arm64 python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy application code
COPY . /app/

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
