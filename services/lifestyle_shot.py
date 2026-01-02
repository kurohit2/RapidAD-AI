from typing import Dict, Any, Optional, List
import requests
import base64
import os
import io
from PIL import Image
try:
    import google.generativeai as genai
except ImportError:
    genai = None

def merge_vision_and_prompt(
    gemini_api_key: str,
    ref_image_data: str,  # Base64 or URL
    user_prompt: str
) -> str:
    """
    Use Gemini 1.5 Pro to analyze a reference image and a user prompt,
    merging them into a single high-quality studio photoshoot description.
    """
    if not genai or not gemini_api_key:
        return user_prompt

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prepare the image for Gemini
        img = None
        if ref_image_data.startswith('data:image'):
            base64_data = ref_image_data.split(",", 1)[1]
            img = Image.open(io.BytesIO(base64.b64decode(base64_data)))
        elif ref_image_data.startswith('http'):
            # For brevity, Gemini 1.5 Pro handles URLs via its own ecosystem 
            # or we fetch it. Let's fetch it for reliability.
            response = requests.get(ref_image_data)
            img = Image.open(io.BytesIO(response.content))
        else:
            # Assume local path if not URL/Base64
            if os.path.exists(ref_image_data):
                img = Image.open(ref_image_data)

        prompt_text = f"""
        Act as a Professional Product Photographer.
        1. ANALYZE THE REFERENCE IMAGE: Identify the exact physical surface (e.g. wooden table, marble floor), the perspective (e.g. eye-level, top-down), and the lighting.
        2. ANALYZE THE USER REQUEST: "{user_prompt}"
        3. MERGE THEM: Create a single, detailed prompt that recreates the EXACT setting of the reference image but incorporates the user's specific request.
        
        CRITICAL: The product must be naturally placed ON the physical surface from the reference image.
        Describe the materials, textures, and camera depth (e.g. 'sharp focus on the product on the rustic wooden surface, soft bokeh background').
        
        Output ONLY the final merged prompt string.
        """
        
        content = [prompt_text]
        if img:
            content.append(img)
            
        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini prompt merging failed: {str(e)}")
        return user_prompt
def lifestyle_shot_by_text(
    api_key: str,
    image_data: bytes,
    scene_description: str,
    placement_type: str = "original",
    num_results: int = 4,
    sync: bool = False,
    fast: bool = True,
    optimize_description: bool = True,
    original_quality: bool = False,
    exclude_elements: Optional[str] = None,
    shot_size: List[int] = [1000, 1000],
    manual_placement_selection: List[str] = ["upper_left"],
    padding_values: List[int] = [0, 0, 0, 0],
    foreground_image_size: Optional[List[int]] = None,
    foreground_image_location: Optional[List[int]] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    sku: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using text description.
    
    Args:
        api_key: Bria AI API key
        image_data: Image data in bytes
        scene_description: Text description of the new scene
        placement_type: How to position the product ("original", "automatic", "manual_placement", "manual_padding", "custom_coordinates")
        num_results: Number of results to generate
        sync: Whether to wait for results
        fast: Whether to use fast mode
        optimize_description: Whether to optimize the scene description
        original_quality: Whether to maintain original image quality
        exclude_elements: Elements to exclude from generation
        shot_size: Size of the output image [width, height]
        manual_placement_selection: List of placement positions
        padding_values: Padding values [left, right, top, bottom]
        foreground_image_size: Size of foreground image [width, height]
        foreground_image_location: Position of foreground image [x, y]
        force_rmbg: Whether to force background removal
        content_moderation: Whether to enable content moderation
        sku: Optional SKU identifier
    """
    url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_text"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Convert image to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Prepare request data
    data = {
        'file': image_base64,
        'scene_description': scene_description,
        'placement_type': placement_type,
        'num_results': num_results,
        'sync': sync,
        'fast': fast,
        'optimize_description': optimize_description,
        'original_quality': original_quality,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation
    }
    
    # Add optional parameters
    if exclude_elements and not fast:
        data['exclude_elements'] = exclude_elements
    
    if placement_type in ['automatic', 'manual_placement', 'custom_coordinates']:
        data['shot_size'] = shot_size
    
    if placement_type == 'manual_placement':
        data['manual_placement_selection'] = manual_placement_selection
    
    if placement_type == 'manual_padding':
        data['padding_values'] = padding_values
    
    if placement_type == 'custom_coordinates':
        if foreground_image_size:
            data['foreground_image_size'] = foreground_image_size
        if foreground_image_location:
            data['foreground_image_location'] = foreground_image_location
    
    if sku:
        data['sku'] = sku
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.json()
    except Exception as e:
        raise Exception(f"Lifestyle shot generation failed: {str(e)}")

def generate_product_shot(
    api_key: str,
    image_data: str,  # Base64 string (with data: prefix) or URL
    ref_image_data: str,  # Base64 string (with data: prefix) or URL
    scene_description: str = None,
    gemini_api_key: str = None,  # For Smart Prompt Merger
    num_results: int = 4,
    sync: bool = False,
    force_rmbg: bool = False,
    content_moderation: bool = False
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using Bria's best available endpoint.
    If BOTH prompt and reference are provided, uses Gemini to merge them.
    """
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Prepare standard image parameter
    def _prepare_image(data: str):
        if not data: return None, None
        if data.startswith('data:image'):
            try:
                base64_data = data.split(",", 1)[1]
                return 'file', base64_data
            except:
                return 'url', data
        elif data.startswith('http'):
            return 'url', data
        else:
            # Check if it's a local file (strip leading slash if present for relative path)
            clean_path = data.lstrip('/')
            if os.path.exists(clean_path):
                try:
                    with open(clean_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                        return 'file', b64
                except Exception as e:
                    print(f"Failed to read local file {clean_path}: {e}")
            
            # Fallback to assuming it's already base64 or a path that Bria should handle (unlikely)
            return 'file', data

    # Prepare standard product image
    data = {
        'num_results': num_results,
        'sync': sync,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation
    }
    prod_key, prod_val = _prepare_image(image_data)
    if prod_key == 'file': data['file'] = prod_val
    else: data['image_url'] = prod_val

    # DEFINE THE DEFAULT STUDIO PROMPT
    DEFAULT_PROMPT = "High-end studio product photography, professional lighting, photorealistic, integrated shadows, 8k."
    
    # Check if the prompt is customized
    is_custom_prompt = scene_description and scene_description.strip() != DEFAULT_PROMPT.strip()
    
    # SMART ROUTING DECISION
    # 1. EXACT COMPOSITION: use by_image if no custom prompt provided.
    #    Bria will place the product exactly on the surface of the reference image.
    if not is_custom_prompt and ref_image_data:
        print("🎯 Using Exact Composition route (by_image)...")
        url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_image"
        ref_key, ref_val = _prepare_image(ref_image_data)
        if ref_key == 'file': data['ref_image_file'] = ref_val
        else: data['ref_image_url'] = ref_val
        
    # 2. CREATIVE MERGE: use Gemini + by_text if custom prompt provided.
    elif is_custom_prompt and ref_image_data and gemini_api_key:
        print("🤖 Gemini is merging your template and custom prompt...")
        merged_prompt = merge_vision_and_prompt(
            gemini_api_key, 
            ref_image_data, 
            scene_description
        )
        url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_text"
        data['scene_description'] = merged_prompt
        # We clear ref_image_data ONLY for the by_text route to avoid Bria 400 error
        # but the "vision" of the ref image is now inside the merged_prompt.
        
    # 3. TEXT ONLY: fallback/prompt-only
    elif scene_description:
        print("📝 Using Text-only route (by_text)...")
        url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_text"
        data['scene_description'] = scene_description
        
    else:
        # Fallback to image route if somehow prompt is default but image provided
        url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_image"
        if ref_image_data:
            ref_key, ref_val = _prepare_image(ref_image_data)
            if ref_key == 'file': data['ref_image_file'] = ref_val
            else: data['ref_image_url'] = ref_val

    # Set placement to automatic if the product is a cutout for better results
    # or 'original' to keep the Tab 1 position. Let's stick to original as 
    # the user is likely providing a centered cutout.
    data['placement_type'] = 'original'

    # DEBUG LOGGING
    print(f"--- Bria Request Debug ---")
    print(f"URL: {url}")
    print(f"Custom Prompt: {is_custom_prompt}")
    print(f"Data Keys: {list(data.keys())}")
    # Don't print full base64 strings as they are too huge, just lengths
    if 'file' in data: print(f"File length: {len(data['file'])}")
    if 'ref_image_file' in data: print(f"Ref Image length: {len(data['ref_image_file'])}")
    if 'scene_description' in data: print(f"Scene Description: {data['scene_description']}")
    print(f"--------------------------")

    try:
        response = requests.post(url, headers=headers, json=data)
        
        # LOGGING
        print(f"Bria Request to {url}")
        print(f"Bria Status: {response.status_code}")
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        status_code = getattr(e.response, "status_code", 400) if hasattr(e, "response") and e.response is not None else 400
        try:
            response_text = e.response.text if hasattr(e, "response") and e.response is not None else str(e)
            try:
                error_json = e.response.json()
                return {"error": error_json, "status_code": status_code, "url_attempted": url}
            except:
                return {"error": response_text, "status_code": status_code, "url_attempted": url}
        except:
            raise Exception(f"Product shot generation failed: {str(e)}")

def lifestyle_shot_by_image(
    api_key: str,
    image_data: bytes,
    reference_image: bytes,
    placement_type: str = "original",
    num_results: int = 4,
    sync: bool = False,
    original_quality: bool = False,
    shot_size: List[int] = [1000, 1000],
    manual_placement_selection: List[str] = ["upper_left"],
    padding_values: List[int] = [0, 0, 0, 0],
    foreground_image_size: Optional[List[int]] = None,
    foreground_image_location: Optional[List[int]] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    sku: Optional[str] = None,
    enhance_ref_image: bool = True,
    ref_image_influence: float = 1.0
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using a reference image.
    """
    url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_image"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Convert images to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    reference_base64 = base64.b64encode(reference_image).decode('utf-8')
    
    # Prepare request data
    data = {
        'file': image_base64,
        'ref_image_file': reference_base64,
        'placement_type': placement_type,
        'num_results': num_results,
        'sync': sync,
        'original_quality': original_quality,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation,
        'enhance_ref_image': enhance_ref_image,
        'ref_image_influence': ref_image_influence
    }
    
    # Add optional parameters
    if placement_type in ['automatic', 'manual_placement', 'custom_coordinates']:
        data['shot_size'] = shot_size
    
    if placement_type == 'manual_placement':
        data['manual_placement_selection'] = manual_placement_selection
    
    if placement_type == 'manual_padding':
        data['padding_values'] = padding_values
    
    if placement_type == 'custom_coordinates':
        if foreground_image_size:
            data['foreground_image_size'] = foreground_image_size
        if foreground_image_location:
            data['foreground_image_location'] = foreground_image_location
    
    if sku:
        data['sku'] = sku
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.json()
    except Exception as e:
        raise Exception(f"Lifestyle shot generation failed: {str(e)}") 