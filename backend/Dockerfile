FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build-essential for C++11 support
#RUN apt-get update && apt-get install -y \
#    python3-dev \
#    build-essential

# Copy the install dependencies and install
ADD pyproject.toml /app/
ADD .python-version /app/
ADD uv.lock /app/
WORKDIR /app
RUN uv sync --frozen

# Copy the project files into the image
ADD api/ /app/api/
ADD backend/ /app/backend/
ADD manage.py /app/

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]