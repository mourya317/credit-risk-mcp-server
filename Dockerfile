FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variable to enable HTTP mode
ENV MCP_HTTP_MODE=true

# Cloud Run will set PORT environment variable
CMD exec gunicorn --bind :$PORT --worker-class=uvicorn.workers.UvicornWorker --workers 1 --threads 8 --timeout 0 src.credit_risk_api:app