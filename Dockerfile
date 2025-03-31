# Use official Python image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all files to /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run Flask application
CMD ["python", "app.py"]
