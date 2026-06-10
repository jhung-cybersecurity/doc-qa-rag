# Base image: slim = Debian + Python, no extra bloat (~150MB vs ~1GB)
FROM python:3.12-slim

# The working directory inside the container. All later paths are relative to this.
WORKDIR /app

# Copy ONLY requirements first. This layer caches and won't rebuild
# when you change code, so installs don't re-run every build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the app code and data. These change often, so they go last.
COPY src/ ./src/
COPY data/ ./data/

# Documents which port the app listens on (informational)
EXPOSE 8000

# Startup command. fastapi run uses Uvicorn under the hood and
# binds to 0.0.0.0 by default (required so the container is reachable).
CMD ["fastapi", "run", "src/api.py", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

  