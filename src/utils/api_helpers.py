from typing import Dict, Any, Optional

def format_response(response: Dict[str, Any]) -> str:
    """Format an API response into a readable string."""
    if not response or "error" in response:
        return f"Error: {response.get('message', 'Unknown error')}"
    
    # Pretty format the response
    result = ""
    for key, value in response.items():
        if isinstance(value, dict):
            result += f"{key}:\n"
            for sub_key, sub_value in value.items():
                result += f"  {sub_key}: {sub_value}\n"
        elif isinstance(value, list):
            result += f"{key}:\n"
            for item in value:
                if isinstance(item, dict):
                    for item_key, item_value in item.items():
                        result += f"  - {item_key}: {item_value}\n"
                else:
                    result += f"  - {item}\n"
        else:
            result += f"{key}: {value}\n"
    
    return result
