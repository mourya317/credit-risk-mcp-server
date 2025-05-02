from typing import Any, Dict, List, Optional
import httpx
import ssl
import json
import sys
import os
from mcp.server.fastmcp import FastMCP
from flask import Flask, request, jsonify, Response
import asyncio
import time

ssl_context = ssl.create_default_context()
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2  # Ensure TLS 1.2 or higher
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Initialize FastMCP server
mcp = FastMCP("paypal-credit")

# Flask app for HTTP mode
app = Flask(__name__)

# Constants
BASE_URL = "https://msmaster.qa.paypal.com:21994"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "CORRELATION-ID": "mcp-correlation-id",
    "PAYPAL-REQUEST-ID": "mcp-request-id",
    "PayPal-Entry-Point": "http://uri.paypal.com/API_MOBILE/Web/NodeJS/POST/v1/onboarding/create-entities",
    "Paypal-Remote-Address": "123456789",
    "cache-control": "no-cache",
    "paypal-client-metadata-id": "mcp-client-id",
    "Paypal-Client-Ipaddress": "10.23.14.15"
}

# Security context for API calls
DEFAULT_SECURITY_CONTEXT = {
    "X-PAYPAL-SECURITY-CONTEXT": json.dumps({
        "subjects": [{
            "subject": {
                "external_id": "venmoaccountnumber1234",
                "account_number": "1911197561074631328",
                "actor": {
                    "client_id": "AYxSef8wNXn6JNjjuiluQWN1F9qa2RHYnkx0aKqpPyZyFWTO6559hikB74xQCiswwU_UsYKEpjgr56qE",
                    "id": "9003007",
                    "auth_claims": ["CLIENT_ID_SECRET"],
                    "auth_state": "LOGGEDIN",
                    "account_number": "2109864994628634312",
                    "encrypted_account_number": "KP9C3ZXWARJUU",
                    "party_id": "2109864994628634312",
                    "user_type": "API_CALLER",
                    "tenant_context": {
                        "tenant_name": "VENMO",
                        "tenant_id": "37ceb41a-92fb-40cd-821f-67a362005d61"
                    },
                    "legal_country": "US"
                },
                "account_access_privilege": {
                    "access_class": "GUEST",
                    "type": "ANONYMOUS"
                },
                "tenant_context": {
                    "tenant_name": "VENMO",
                    "tenant_id": "venmoid12345"
                }
            }
        }]
    })
}


async def make_api_request(method: str, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to the PayPal API with proper error handling."""
    headers = {**DEFAULT_HEADERS, **DEFAULT_SECURITY_CONTEXT}
    
    async with httpx.AsyncClient(verify=True, timeout=30.0) as client:
        try:
            if method.upper() == "POST":
                response = await client.post(url, json=data, headers=headers, timeout=30.0)
            elif method.upper() == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": f"HTTP error: {e.response.text}"
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Request failed: {str(e)}"
            }


@mcp.tool()
async def evaluate_credit_approvability(
    email: str,
    full_name: str,
    given_name: str,
    surname: str,
    country_code: str = "1",
    phone_number: str = "3046738654",
    user_id: str = "110171134",
    product_id: str = "CREDIT_CARD_US",
    use_mock: bool = True  # Add this parameter with default True
) -> str:
    """
    Evaluate credit approvability for a customer.

    Args:
        email: Customer's email address
        full_name: Customer's full name
        given_name: Customer's first name
        surname: Customer's last name
        country_code: Phone country code (default: "1" for US)
        phone_number: Customer's phone number
        user_id: Customer's ID in the system
        product_id: Type of credit product (default: CREDIT_CARD_US)
        use_mock: Use mock data instead of calling real API (for testing)
    """
    # Use mock response for testing due to SSL issues
    if use_mock:
        # Generate mock response based on customer data
        is_approved = "john" in full_name.lower() or "john" in email.lower()
        
        if is_approved:
            return """
Credit Approvability Decision: APPROVED
Reason: Customer meets eligibility criteria

Eligible: True
"""
        else:
            return """
Credit Approvability Decision: DECLINED
Reason: Credit risk score below threshold

Eligible: False
Ineligibility Reasons:
- Low credit score
- Limited credit history
"""
    
    # Only proceed to the real API if not using mock
    url = f"{BASE_URL}/v1/risk/evaluate-credit-approvability"
    
    # Construct the payload based on the Postman collection
    payload = {
        "context": {
            "product": {
                "country_code": "US",
                "product_id": product_id
            },
            "product_experience": {
                "channel": "MOBILE_APP",
                "product_flow": "CREDIT_APPROVABILITY"
            }
        },
        "mode": "NO_VENDOR_SCREENING",
        "prospect": {
            "emails": [
                {
                    "email_address": email
                }
            ],
            "id": user_id,
            "names": [
                {
                    "full_name": full_name,
                    "given_name": given_name,
                    "surname": surname
                }
            ],
            "phones": [
                {
                    "country_code": country_code,
                    "national_number": phone_number,
                    "type": "MOBILE"
                }
            ]
        },
        "risk_signals": {
            "scores": [
                {
                    "name": "CREDIT_PROPENSITY",
                    "value": "0"
                }
            ]
        }
    }
    
    response = await make_api_request("POST", url, payload)
    
    if response.get("error"):
        return f"Error evaluating credit approvability: {response.get('message')}"
    
    # Format the response in a user-friendly way
    try:
        decision = response.get("decision", {})
        decision_type = decision.get("type", "UNKNOWN")
        reason = decision.get("reason", "No reason provided")
        
        result = f"Credit Approvability Decision: {decision_type}\n"
        result += f"Reason: {reason}\n\n"
        
        # Add any additional details if available
        if "eligibility" in response:
            eligibility = response["eligibility"]
            result += f"Eligible: {eligibility.get('eligible', False)}\n"
            if "ineligibility_reasons" in eligibility:
                reasons = eligibility["ineligibility_reasons"]
                if reasons:
                    result += "Ineligibility Reasons:\n"
                    for r in reasons:
                        result += f"- {r.get('description', 'Unknown reason')}\n"
        
        return result
    except Exception as e:
        return f"Success, but failed to parse response: {str(e)}\nRaw response: {response}"


# HTTP route handler for Cloud Run
@app.route('/mcp', methods=['POST'])
def handle_mcp_request():
    # Get the MCP request from the HTTP body
    mcp_request = request.json
    
    # Process the request using MCP
    method = mcp_request.get('method')
    params = mcp_request.get('params', {})
    
    if method == 'evaluate_credit_approvability':
        # Use asyncio to run the async function from synchronous code
        import asyncio
        result = asyncio.run(evaluate_credit_approvability(**params))
        return jsonify({"result": result})
    else:
        return jsonify({"error": f"Unknown method: {method}"})
    

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})    


# Add this new SSE endpoint
@app.route('/mcp/sse', methods=['GET'])
def sse_endpoint():
    def generate():
        # Send an initial message to establish the connection
        yield "data: {\"type\": \"connection_established\"}\n\n"
        
        # Keep the connection alive
        while True:
            # Wait for next request
            # In a real implementation, you would have a queue system here
            # This is a simplified example that just keeps the connection open
            yield "data: {\"type\": \"keepalive\"}\n\n"
            time.sleep(30)  # Send keepalive every 30 seconds
    
    return Response(generate(), mimetype="text/event-stream")

# Add this endpoint to receive MCP commands when using SSE
@app.route('/mcp/command', methods=['POST'])
def handle_sse_command():
    # Get the MCP request from the HTTP body
    mcp_request = request.json
    
    # Process the request using MCP
    method = mcp_request.get('method')
    params = mcp_request.get('params', {})
    
    if method == 'evaluate_credit_approvability':
        # Use asyncio to run the async function from synchronous code
        import asyncio
        result = asyncio.run(evaluate_credit_approvability(**params))
        return jsonify({"result": result})
    else:
        return jsonify({"error": f"Unknown method: {method}"})

if __name__ == "__main__":
    # Check if we're running in HTTP mode (for Cloud Run)
    if os.environ.get("MCP_HTTP_MODE", "false").lower() == "true":
        # Get port from environment variable (Cloud Run sets PORT)
        port = int(os.environ.get("PORT", 8080))
        # Use debug=False for production
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        # Initialize and run the server in stdio mode
        print("PayPal Credit MCP Server Started")
        mcp.run(transport="stdio")
