# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8080 (Koyeb expects your app to listen on port 8080)
EXPOSE 8080

# Use gunicorn to serve your app.
# Ensure your Flask app’s main file (e.g., app.py) exposes a WSGI callable named `app`
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]


