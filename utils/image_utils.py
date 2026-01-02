import base64
import os

def image_to_base64(image_input):
    """
    Convert image input (bytes, file path, or file-like object) to base64 string.
    """
    if not image_input:
        return None
        
    if isinstance(image_input, bytes):
        return base64.b64encode(image_input).decode('utf-8')
        
    if isinstance(image_input, str) and os.path.exists(image_input):
        with open(image_input, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    # If it's a file-like object (like Streamlit UploadedFile)
    if hasattr(image_input, "read"):
        return base64.b64encode(image_input.read()).decode('utf-8')
        
    return None
