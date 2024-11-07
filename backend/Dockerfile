FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build-essential for C++11 support
#RUN apt-get update && apt-get install -y \
#    python3-dev \
#    build-essential

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]