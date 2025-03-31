# Use lightweight Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . /app/

# Expose port 5000
EXPOSE 5000

# Run Flask application
CMD ["python", "app.py"]
# Use lightweight Nginx image
FROM nginx:alpine   