FROM python:3.14-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY main.py ./
COPY src/ ./src/

# Install uv
RUN pip install uv

# Install dependencies
RUN uv pip install --system -e .

# Run the bot
CMD ["python", "main.py"]
