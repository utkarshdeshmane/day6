# Use Python 3.9 slim as base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application to the container
COPY . /app

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Copy Nginx config
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Expose Flask app on 8000 and Nginx on 80
EXPOSE 80 8000

# Start Flask and Nginx
CMD service nginx start && python app.py
