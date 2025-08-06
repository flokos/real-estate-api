FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies + curl for Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry globally
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry files first for dependency caching
COPY pyproject.toml poetry.lock*  README.md ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the Django project folder
COPY . /app/

# Expose port
EXPOSE 8000

RUN python manage.py collectstatic --noinput

# Run migrations and start the development server
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
