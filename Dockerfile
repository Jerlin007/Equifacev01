# Use lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for dlib & opencv
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port for Flask
EXPOSE 8080

# Run the app on port 8080 (Koyeb default)
CMD ["python", "app.py"]
