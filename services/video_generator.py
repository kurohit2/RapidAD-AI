import time
import os
import replicate
import requests
from typing import Optional, Dict, Any

def generate_video_with_replicate(
    api_token: str,
    image_data: Any,  # Bytes or URL
    prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a video from a lifestyle shot using Replicate (Stable Video Diffusion).
    """
    try:
        # Set API Token
        os.environ["REPLICATE_API_TOKEN"] = api_token
        
        # Prepare the image. Replicate's SDK can take a file handle or URL.
        # If it's bytes, we need to provide a file-like object.
        import io
        if isinstance(image_data, bytes):
            image_input = io.BytesIO(image_data)
        else:
            image_input = image_data

        print(f"🎬 Starting Replicate generation (Wan 2.1)...")
        
        # Wan 2.1 image-to-video model (Optimized by Wavespeed)
        model_name = "wavespeedai/wan-2.1-i2v-480p"
        
        # Run the model
        output = replicate.run(
            model_name,
            input={
                "image": image_input,
                "prompt": prompt if prompt else "cinematic product ad video",
                "fast_mode": "Balanced",
                "aspect_ratio": "16:9",
                "fps": 16
            }
        )

        if not output:
            return {"error": "No output URL returned from Replicate."}

        # Stability AI SVD usually returns a URL to the MP4
        return {
            "video_url": output,
            "video_data": output
        }

    except Exception as e:
        error_str = str(e)
        if "NSFW" in error_str:
            return {"error": "❌ **Content Filter Triggered**: Replicate safety filters flagged the content."}
        elif "authentication" in error_str.lower():
            return {"error": "❌ **Authentication Failed**: Please check your Replicate API Token."}
        return {"error": f"Failed to generate video (Replicate): {error_str}"}
