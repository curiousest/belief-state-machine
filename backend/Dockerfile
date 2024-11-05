# backend/Dockerfile
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the poetry configuration files
COPY backend/pyproject.toml backend/poetry.lock ./

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - && \
    # Add poetry to PATH
    export PATH="/root/.local/bin:$PATH" && \
    # Install dependencies
    poetry install --no-root

# Copy the rest of the application code
COPY backend/ .

# Command to run the application
CMD ["python", "manage.py", "runserver"]
