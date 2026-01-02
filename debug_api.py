import requests
import json

def test_api(name, endpoint, method="GET", json_data=None, form_data=None):
    url = f"http://127.0.0.1:5000{endpoint}"
    print(f"\n--- Testing {name} ({method} {endpoint}) ---")
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            if json_data:
                response = requests.post(url, json=json_data)
            else:
                response = requests.post(url, data=form_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print("Response Content (first 500 chars):")
        print(response.text[:500])
        
        try:
            data = response.json()
            print("Successfully parsed as JSON.")
        except Exception as e:
            print(f"FAILED to parse as JSON: {e}")
            if "<!doctype" in response.text.lower():
                print("Observed HTML Doctype. This is likely a Flask error page or a 404.")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api("List Templates", "/api/list_templates")
    test_api("Enhance Prompt", "/api/enhance_prompt", "POST", json_data={"prompt": "apple"})
    test_api("Generate HD", "/api/generate_hd", "POST", json_data={"prompt": "apple", "aspect_ratio": "1:1"})
    test_api("Process Photography (Fail Case)", "/api/process_photography", "POST", form_data={"operation": "remove_bg"})
    test_api("CTA Overlay (Fail Case)", "/api/cta_overlay", "POST", json_data={"image_url": "invalid"})
    test_api("Generate Video (Fail Case)", "/api/generate_video", "POST", json_data={"image_url": "invalid", "prompt": "zoom"})
