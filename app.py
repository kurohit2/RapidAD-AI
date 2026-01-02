import os
import time
import base64
import requests
import io
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as st_genai
from google import genai
from PIL import Image

# Import services
from services.hd_image_generation import generate_hd_image
from services.lifestyle_shot import generate_product_shot, lifestyle_shot_by_text, lifestyle_shot_by_image
from services.shadow import add_shadow
from services.packshot import create_packshot
from services.background_removal import remove_background
from services.prompt_enhancement import enhance_prompt
from utils.image_utils import image_to_base64
from utils.text_overlay import add_cta_to_image

# Load environment variables
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API Keys
BRIA_API_KEY = os.getenv("BRIA_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
st_genai.configure(api_key=GOOGLE_API_KEY)

# --- UTILS ---
def download_image(url):
    if not url: return None
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Download failed: {e}")
        return None

def _extract_urls(data):
    """Robustly extract all image URLs from various Bria response formats"""
    urls = []
    if not isinstance(data, dict): return urls
    if "result_urls" in data and isinstance(data["result_urls"], list):
        urls.extend(data["result_urls"])
    elif "result_url" in data:
        urls.append(data["result_url"])
    elif "result" in data and isinstance(data["result"], list):
        for item in data["result"]:
            if isinstance(item, dict):
                if "urls" in item and len(item["urls"]) > 0: urls.append(item["urls"][0])
                elif "url" in item: urls.append(item["url"])
            elif isinstance(item, list) and len(item) > 0: urls.append(item[0])
            elif isinstance(item, str): urls.append(item)
    elif "urls" in data and isinstance(data["urls"], list):
        urls.extend(data["urls"])
    return urls

# --- FLASK ROUTES ---
@app.route('/api/list_templates')
def api_list_templates():
    template_dir = os.path.join('assets', 'templates')
    if not os.path.exists(template_dir):
        return jsonify([])
    templates = [f for f in os.listdir(template_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return jsonify(templates)

@app.route('/assets/templates/<path:filename>')
def serve_template(filename):
    return send_from_directory('assets/templates', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate_hd', methods=['POST'])
def api_generate_hd():
    prompt = request.json.get('prompt')
    aspect_ratio = request.json.get('aspect_ratio', '1:1')
    style = request.json.get('style', 'photography')
    
    try:
        result = generate_hd_image(
            prompt=prompt,
            api_key=BRIA_API_KEY,
            aspect_ratio=aspect_ratio,
            medium=style,
            sync=True
        )
        urls = _extract_urls(result)
        return jsonify({
            "urls": urls,
            "result_url": urls[0] if urls else None,
            "raw": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/enhance_prompt', methods=['POST'])
def api_enhance():
    prompt = request.json.get('prompt')
    try:
        # We can still use st_genai here if Bria service is not available
        # or just stick to the original plan of Bria if enhance_prompt is imported
        result = enhance_prompt(BRIA_API_KEY, prompt)
        return jsonify({"enhanced_prompt": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process_photography', methods=['POST'])
def api_process_photography():
    image_url = request.form.get('image_url')
    image_file = request.files.get('image')
    operation = request.form.get('operation')
    
    if image_file:
        img_bytes = image_file.read()
    elif image_url:
        img_bytes = download_image(image_url)
    else:
        return jsonify({"error": "No image provided"}), 400

    try:
        if operation == "remove_bg":
            if image_url:
                result = remove_background(BRIA_API_KEY, image_url=image_url)
            else:
                result = remove_background(BRIA_API_KEY, image_data=img_bytes)
        elif operation == "packshot":
            bg_color = request.form.get('bg_color', '#FFFFFF')
            result = create_packshot(BRIA_API_KEY, img_bytes, background_color=bg_color)
        elif operation == "shadow":
            intensity = int(request.form.get('intensity', 60))
            result = add_shadow(BRIA_API_KEY, img_bytes, shadow_intensity=intensity)
        elif operation == "lifestyle":
            prompt = request.form.get('prompt', '')
            ref_url = request.form.get('ref_url')
            
            # If ref_url is a relative template path, make it absolute or ensure it's relative to app root
            if ref_url and ref_url.startswith('/assets/templates/'):
                ref_url = ref_url.lstrip('/')
            
            # Use the consolidated generate_product_shot which handles ref image
            result = generate_product_shot(
                api_key=BRIA_API_KEY,
                image_data=image_to_base64(img_bytes),
                ref_image_data=ref_url if ref_url else None,
                scene_description=prompt,
                gemini_api_key=GOOGLE_API_KEY,
                sync=True
            )
            
            if isinstance(result, dict) and "error" in result:
                return jsonify(result), result.get("status_code", 500)
        else:
            return jsonify({"error": "Invalid operation"}), 400
        
        urls = _extract_urls(result)
        return jsonify({
            "urls": urls,
            "result_url": urls[0] if urls else (result.get('result_url') if isinstance(result, dict) else None),
            "raw": result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/cta_overlay', methods=['POST'])
def api_cta_overlay():
    image_url = request.json.get('image_url')
    headline = request.json.get('headline', '')
    subheadline = request.json.get('subheadline', '')
    
    img_bytes = download_image(image_url)
    if not img_bytes: return jsonify({"error": "Failed to get image"}), 400
    
    try:
        result_bytes = add_cta_to_image(img_bytes, headline, subheadline)
        b64 = base64.b64encode(result_bytes).decode('utf-8')
        return jsonify({"result_b64": f"data:image/png;base64,{b64}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_video', methods=['POST'])
def api_generate_video():
    image_url = request.json.get('image_url')
    prompt = request.json.get('prompt')
    aspect_ratio = request.json.get('aspect_ratio', '16:9')
    duration = request.json.get('duration', '5')
    
    if not image_url or not prompt:
        return jsonify({"error": "Missing data"}), 400

    try:
        img_bytes = download_image(image_url)
        img = Image.open(io.BytesIO(img_bytes))
        
        # Using the new google-genai v1 SDK for Veo 3.1
        client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
        
        # Configuration for Veo
        config = {
            'duration_seconds': int(duration),
            'aspect_ratio': aspect_ratio,
        }
        
        # Trigger generation
        operation = client.models.generate_videos(
            model='veo-3.1-generate-001',
            prompt=prompt,
            image=img,
            config=config
        )
        
        # Async polling (10s intervals)
        for _ in range(40): # ~7 mins max
            time.sleep(10)
            status = client.operations.get(name=operation.name)
            if status.done:
                if status.error:
                    return jsonify({"error": str(status.error)}), 500
                return jsonify({"video_url": status.response.generated_videos[0].video.uri})
        
        return jsonify({"error": "Timeout"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
