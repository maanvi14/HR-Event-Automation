import requests
import os
from PIL import Image
from io import BytesIO

def download_photo(url_or_id, name):
    os.makedirs("photos", exist_ok=True)
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Extract File ID
    file_id = url_or_id
    if "drive.google.com" in url_or_id:
        if "id=" in url_or_id:
            file_id = url_or_id.split("id=")[-1].split("&")[0]
        elif "/d/" in url_or_id:
            file_id = url_or_id.split("/d/")[1].split("/")[0]
    
    file_id = file_id.strip()
    # Use docs.google.com for better API reliability
    base_url = "https://docs.google.com/uc?export=download"
    
    try:
        print(f"🌐 Fetching ID: {file_id}")
        # First request to get cookies
        response = session.get(base_url, params={'id': file_id}, headers=headers, stream=True)
        
        # Check for Google's "Confirm" token
        confirm_token = None
        for key, value in response.cookies.items():
            if 'download_warning' in key:
                confirm_token = value
                break
        
        if confirm_token:
            response = session.get(base_url, params={'id': file_id, 'confirm': confirm_token}, headers=headers, stream=True)

        if response.status_code != 200:
            raise Exception(f"Google returned status {response.status_code}")

        # Validate Image
        image = Image.open(BytesIO(response.content))
        ext = image.format.lower() if image.format else "png"
        ext = "jpg" if ext == "jpeg" else ext
        
        path = os.path.join("photos", f"{name.replace(' ', '_')}.{ext}")
        
        # Convert and Save
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
            
        image.save(path)
        print(f"✅ Photo saved: {path}")
        return os.path.abspath(path)

    except Exception as e:
        print(f"❌ FETCH ERROR: {e}")
        raise Exception(f"Image download failed: {str(e)}")
    
    