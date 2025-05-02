# PayPal Credit MCP Server

This project provides an MCP wrapper around PayPal Credit Risk APIs.

## Features

- Evaluate credit approvability

## Development

### Prerequisites

- Python 3.9+
- Docker (for containerization)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd credit-risk-mcp-server
   ```

2. Install dependencies:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Run the application locally:
   ```bash
   python src/main.py
   ```

## Deployment

To deploy the application to Google Cloud Run, follow these steps:

1. Build the Docker image:
   ```bash
   docker build -t gcr.io/<your-project-id>/credit-risk-mcp-server .
   ```

2. Push the Docker image to Google Container Registry:
   ```bash
   docker push gcr.io/<your-project-id>/credit-risk-mcp-server
   ```

3. Deploy to Google Cloud Run:
   ```bash
   gcloud run deploy credit-risk-mcp-server \
     --image gcr.io/<your-project-id>/credit-risk-mcp-server \
     --platform managed \
     --region <your-region> \
     --allow-unauthenticated
   ```

   Or simply use the provided deployment script:
   ```bash
   ./deploy.sh
   ```
   (Make sure to update the PROJECT_ID in the script first)

## Usage

Once deployed, you can access the FastMCP server via the URL provided by Google Cloud Run. You can use the endpoints to access PayPal Credit services through the Machine Conversation Protocol interface.

### Available Tools

#### Credit Risk API
- `evaluate_credit_approvability` - Evaluate credit approvability for a customer

## Testing

Run the tests using pytest:
```bash
pytest src/tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.
