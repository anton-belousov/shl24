FROM python:3.12-slim

ENV BRAVE_SEARCH_API_KEY=""
ENV YANDEX_API_KEY=""
ENV YANDEX_FOLDER_ID=""
ENV WEAVIATE_HOST=""
ENV WEAVIATE_PORT=""

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .
RUN rm .env

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["bash", "run.sh"]
