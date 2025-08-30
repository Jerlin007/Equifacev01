# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --only-binary=:all: --no-deps -r requirements.txt \
    && pip install torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu
# Copy project files
COPY . .

# Expose port 8080 for Koyeb
EXPOSE 8080

# Run the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
