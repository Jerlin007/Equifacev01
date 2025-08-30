# Use slim Python image to avoid unnecessary stuff
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV, dlib, mediapipe
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Use Koyeb's PORT env variable (default to 5000 locally)
ENV PORT=5000

# Expose port (for documentation, Koyeb overrides this internally)
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
