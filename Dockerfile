FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variable to enable HTTP mode
ENV MCP_HTTP_MODE=true

# Use standard Gunicorn without Uvicorn worker
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 src.credit_risk_api:app