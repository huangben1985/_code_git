FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    gcc \
    pulseaudio \
    pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create log directory
RUN mkdir -p ./log

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PULSE_SERVER=unix:/run/pulse/native
ENV PULSE_COOKIE=/root/.config/pulse/cookie

# Command to run the application
CMD ["python", "SpeechMain2.py"] 