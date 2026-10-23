# syntax=docker/dockerfile:1

# ---- Stage 1: "build" — install dependencies; this stage is thrown away later ----
# Pin an exact Python version on the small "slim" variant
FROM python:3.12-slim AS build
# All following commands run inside /app (created if missing)
WORKDIR /app
# Copy ONLY the dependency list first, so this layer stays cached until it changes
COPY requirements.txt .
# Install packages into /install; --no-cache-dir keeps pip's download cache out of the image
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: the final image — starts clean, takes only what it needs ----
FROM python:3.12-slim
WORKDIR /app
# Create an unprivileged user to run the app
RUN useradd --create-home --uid 10001 appuser
# Copy just the installed packages from the build stage
COPY --from=build /install /usr/local
# Copy the application code (after deps, so code edits don't bust the deps cache)
COPY app/ ./app/
# Every command from here on, including the app itself, runs as appuser
USER appuser
# Documents which port the app listens on (it doesn't publish it)
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]