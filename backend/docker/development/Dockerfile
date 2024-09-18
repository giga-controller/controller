FROM python:3.12.1-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Expose port 8080
EXPOSE 8080

# Start Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
