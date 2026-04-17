FROM python:3.11-slim

WORKDIR /app

# Install only what we need - nothing more
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    scikit-learn \
    numpy \
    groq \
    python-dotenv \
    requests

# Copy all project files
COPY . .

# Expose port
EXPOSE 8000

# Start the server
CMD ["python", "backend/main.py"]
