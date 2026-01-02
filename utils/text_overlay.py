from PIL import Image, ImageDraw, ImageFont
import io
import base64

def add_cta_to_image(image_bytes, headline, subheadline, position="bottom", text_color="#FFFFFF", bg_opacity=0.5):
    """
    Overlay CTA text on an image using PIL.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Text overlay layer
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    
    # Try to load a font, fallback to default
    try:
        # Assuming a common font location or default
        font_h = ImageFont.truetype("arial.ttf", int(height * 0.05))
        font_s = ImageFont.truetype("arial.ttf", int(height * 0.03))
    except:
        font_h = ImageFont.load_default()
        font_s = ImageFont.load_default()
    
    # Calculate positions
    h_bbox = d.textbbox((0, 0), headline, font=font_h)
    s_bbox = d.textbbox((0, 0), subheadline, font=font_s)
    
    h_w, h_h = h_bbox[2] - h_bbox[0], h_bbox[3] - h_bbox[1]
    s_w, s_h = s_bbox[2] - s_bbox[0], s_bbox[3] - s_bbox[1]
    
    padding = 20
    rect_h = h_h + s_h + padding * 3
    
    if position == "bottom":
        rect_y = height - rect_h
    else:
        rect_y = 0
        
    # Draw background rectangle
    d.rectangle([0, rect_y, width, rect_y + rect_h], fill=(0,0,0,int(255*bg_opacity)))
    
    # Draw text
    d.text(((width - h_w)/2, rect_y + padding), headline, font=font_h, fill=text_color)
    d.text(((width - s_w)/2, rect_y + h_h + padding * 2), subheadline, font=font_s, fill=text_color)
    
    # Combine
    out = Image.alpha_composite(img, overlay).convert("RGB")
    
    # Save to bytes
    buffer = io.BytesIO()
    out.save(buffer, format="PNG")
    return buffer.getvalue()
