# Use an official Python runtime as a base image
FROM python:3.11-slim
LABEL org.opencontainers.image.source=https://github.com/sireoh/beantrack

# Set the working directory in the container
WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv

# Make sure we use venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application
CMD ["python", "main.py"]