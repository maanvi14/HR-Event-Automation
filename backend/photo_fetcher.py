import requests
import os
from PIL import Image
from io import BytesIO

def download_photo(url_or_id, name):
    os.makedirs("photos", exist_ok=True)
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # ID Cleaning
    file_id = url_or_id.split("id=")[-1].split("/d/")[-1].split("/")[0].split("&")[0].strip()
    
    # Use Thumbnail API for better bot-stability
    base_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"

    try:
        print(f"🌐 Fetching ID: {file_id}")
        response = session.get(base_url, headers=headers, timeout=15)

        if response.status_code != 200:
            raise Exception(f"Google Drive returned {response.status_code}")

        # VALIDATE AND NORMALIZE
        content = response.content
        if b"<html>" in content.lower():
            raise Exception("Google blocked request with an HTML page.")

        # Force normalization to PNG/RGB to kill "unknown format" bugs
        image = Image.open(BytesIO(content)).convert("RGB")
        filename = f"{name.replace(' ', '_')}.png"
        path = os.path.abspath(os.path.join("photos", filename))
        
        image.save(path, "PNG")
        print(f"✅ Photo Normalized: {path}")
        return path

    except Exception as e:
        raise Exception(f"Download Error: {str(e)}")
    
    