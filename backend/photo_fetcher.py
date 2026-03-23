import requests
import os
from PIL import Image
from io import BytesIO

def download_photo(url_or_id, name):
    os.makedirs("photos", exist_ok=True)
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # 1. CLEAN ID EXTRACTION
    file_id = url_or_id
    if "id=" in url_or_id:
        file_id = url_or_id.split("id=")[-1].split("&")[0]
    elif "/d/" in url_or_id:
        file_id = url_or_id.split("/d/")[1].split("/")[0]
    
    file_id = file_id.strip()
    base_url = "https://docs.google.com/uc?export=download"

    try:
        print(f"🌐 Fetching clean ID: {file_id}")
        
        # 2. Get confirmation token for Google virus scan bypass
        response = session.get(base_url, params={'id': file_id}, headers=headers, stream=True)
        confirm_token = None
        for key, value in response.cookies.items():
            if 'download_warning' in key:
                confirm_token = value
                break
        
        if confirm_token:
            response = session.get(base_url, params={'id': file_id, 'confirm': confirm_token}, headers=headers, stream=True)

        if response.status_code != 200:
            raise Exception(f"Google Drive returned {response.status_code}")

        # 3. LOAD AND VALIDATE IMAGE
        # This prevents the "unknown file format" error by ensuring PIL can read the bytes
        image_content = response.content
        image = Image.open(BytesIO(image_content))

        # 4. SAVE
        ext = image.format.lower() if image.format else "png"
        if ext == "jpeg": ext = "jpg"
        
        filename = f"{name.replace(' ', '_')}.{ext}"
        path = os.path.join("photos", filename)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        image.save(path)
        print(f"✅ Photo saved: {path}")
        
        return os.path.abspath(path)

    except Exception as e:
        print(f"❌ DOWNLOAD ERROR: {str(e)}")
        raise Exception(f"Image Error: {str(e)}")
    
    