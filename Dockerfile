FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# install system deps for opencv/mediapipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# install python deps, note we allow --no-deps on mediapipe line
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
