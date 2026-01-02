import requests
import json
import time
import os
import base64
from typing import Optional, Dict, Any, Union
from utils.image_utils import image_to_base64

def get_puter_token() -> Optional[str]:
    """
    Get a temporary Puter.js token (No sign-up required).
    """
    try:
        # Improved headers to avoid 403
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://puter.com",
            "Referer": "https://puter.com/"
        }
        # Based on research, Puter allows temporary signup
        response = requests.post(
            "https://puter.com/signup", 
            json={"is_temp": True},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get('token')
    except Exception as e:
        print(f"Error getting Puter token: {e}")
        return None

def generate_video_with_puter(
    image_data: Any,
    prompt: str,
    model: str = "Wan-AI/Wan2.2-I2V-A14B",
    test_mode: bool = False
) -> Dict[str, Any]:
    """
    Generate a video using Puter.js REST API.
    
    Args:
        image_data: Bytes, URL, or Base64 string of the image.
        prompt: Text prompt for the video.
        model: Model name (e.g., "Wan-AI/Wan2.2-I2V-A14B", "ByteDance/Seedance-1.0-pro").
        test_mode: If True, uses test mode to avoid consuming credits.
        
    Returns:
        Dict containing video_url or error message.
    """
    token = get_puter_token()
    if not token:
        return {"error": "Failed to authenticate with Puter.js (Temporary signup failed)."}

    # Prepare image data
    try:
        if isinstance(image_data, bytes):
            # Convert bytes to base64 for the API if needed, 
            # but Puter might expect a URL. 
            # If we have bytes, we might need to upload it or provide as data URI.
            img_b64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:image/png;base64,{img_b64}"
        elif isinstance(image_data, str) and not image_data.startswith('http'):
            # Assume it's already a data URI or path
            if os.path.exists(image_data):
                img_b64 = image_to_base64(image_data)
                image_url = f"data:image/png;base64,{img_b64}"
            else:
                image_url = image_data # Could be base64 string
        else:
            image_url = image_data # Already a URL
    except Exception as e:
        return {"error": f"Failed to process image data: {str(e)}"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Puter.js txt2vid parameters
    payload = {
        "interface": "puter-txt2vid",
        "driver": "openai-txt2vid", # The wrapper driver for AI services
        "method": "txt2vid",
        "args": {
            "prompt": prompt,
            "model": model,
            "image_url": image_url,
            "test_mode": test_mode
        }
    }

    try:
        print(f"🎬 Calling Puter.js driver: {model}...")
        response = requests.post(
            "https://api.puter.com/drivers/call",
            headers=headers,
            json=payload,
            timeout=300 # Video generation can take time, though usually this returns a job
        )
        response.raise_for_status()
        result = response.json()
        
        # Based on Puter.js behavior, the result might contain the URL or a message
        # If it returns a result object, extract the URL
        if isinstance(result, dict):
            if "result" in result:
                inner_result = result["result"]
                if isinstance(inner_result, str) and (inner_result.startswith('http') or inner_result.startswith('data:video')):
                    return {"video_url": inner_result}
                elif isinstance(inner_result, dict) and "url" in inner_result:
                    return {"video_url": inner_result["url"]}
            
            # If response is direct
            if "url" in result:
                return {"video_url": result["url"]}
            
            if "error" in result:
                return {"error": f"Puter API Error: {result['error']}"}
        
        # If we got something but it's not a URL, return the full result for debugging
        return {"error": f"Unexpected response format from Puter: {result}"}

    except requests.exceptions.HTTPError as e:
        try:
            err_data = e.response.json()
            err_msg = err_data.get('error', {}).get('message', str(e))
        except:
            err_msg = str(e)
        return {"error": f"Puter API HTTP Error: {err_msg}"}
    except Exception as e:
        return {"error": f"Failed to generate video with Puter: {str(e)}"}
