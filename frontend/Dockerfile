# Use a slim Python base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the contents of the 'frontend' directory (not the directory itself) to /app
COPY . /app/

# Install any required dependencies
RUN pip install -r requirements.txt

# Expose the port that the Streamlit app will run on
EXPOSE 8501

# Command to run the Streamlit app and bind it to 0.0.0.0
CMD ["streamlit", "run", "streamlit-app.py", "--server.address=0.0.0.0", "--server.port=8501"]
