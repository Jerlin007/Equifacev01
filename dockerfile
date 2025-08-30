# Use a slim Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies required by mediapipe and OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port (Koyeb listens on $PORT)
EXPOSE 8080

# Start Flask app via gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
