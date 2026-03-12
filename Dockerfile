FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml ./
COPY app ./app
COPY sdk ./sdk

# Install Python dependencies
RUN poetry install --no-interaction --no-dex

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
