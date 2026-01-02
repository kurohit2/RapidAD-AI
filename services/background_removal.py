from typing import Dict, Any
import requests
import base64

def remove_background(
    api_key: str,
    image_data: bytes = None,
    image_url: str = None,
    sync: bool = True,
    content_moderation: bool = False
) -> Dict[str, Any]:
    """
    Remove background from an image using Bria AI.
    
    Args:
        api_key: Bria AI API key
        image_data: Image data in bytes (optional if image_url provided)
        image_url: URL of the image (optional if image_data provided)
        sync: Whether to wait for results
    
    Returns:
        Dict containing the API response
    """
    # Try the most common endpoint first
    url = "https://engine.prod.bria-api.com/v1/background/remove"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Prepare request data
    data = {
        'sync': sync,
        'content_moderation': content_moderation
    }
    
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['file'] = base64.b64encode(image_data).decode('utf-8')
    else:
        raise ValueError("Either image_data or image_url must be provided")
    
    try:
        print(f"Making request to: {url}")
        response = requests.post(url, headers=headers, json=data)
        
        # If 400, try alternative endpoints
        if response.status_code == 400:
            print("Primary endpoint failed with 400, trying alternative v1/remove_background...")
            alt_url = "https://engine.prod.bria-api.com/v1/remove_background"
            response = requests.post(alt_url, headers=headers, json=data)
            
            if response.status_code == 400:
                print("Alternative 1 failed, trying v2/background/remove...")
                alt_url_v2 = "https://engine.prod.bria-api.com/v2/background/remove"
                response = requests.post(alt_url_v2, headers=headers, json=data)

        if response.status_code != 200:
            print(f"Bria Error Status: {response.status_code}")
            print(f"Bria Error Response: {response.text}")
        
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        return response.json()
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
             error_msg = f"{e.response.status_code} - {e.response.text}"
        raise Exception(f"Background removal failed: {error_msg}")
