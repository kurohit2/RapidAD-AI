import os
import requests
from dotenv import load_dotenv
from services.background_removal import remove_background

load_dotenv()
BRIA_API_KEY = os.getenv("BRIA_API_KEY")

def fix_logo():
    logo_path = r"c:\Projects 2025\adsnap\adsnap-flask-pro\static\rapid-logo.png"
    with open(logo_path, "rb") as f:
        img_bytes = f.read()
    
    print("Removing background from logo...")
    result = remove_background(BRIA_API_KEY, image_data=img_bytes)
    
    if "result_url" in result:
        url = result["result_url"]
        print(f"Success! Result URL: {url}")
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(logo_path, "wb") as f:
                f.write(resp.content)
            print("Logo updated with transparent background.")
        else:
            print("Failed to download processed logo.")
    else:
        print(f"Failed to remove background: {result}")

if __name__ == "__main__":
    fix_logo()
