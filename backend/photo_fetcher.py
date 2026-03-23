import requests
import os
from PIL import Image
from io import BytesIO

def download_photo(url_or_id, name):
    os.makedirs("photos", exist_ok=True)
    session = requests.Session()
    # Adding a header makes the request look more like a real browser
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # 1. Extract File ID
    file_id = url_or_id
    if "id=" in url_or_id:
        file_id = url_or_id.split("id=")[-1].split("&")[0]
    elif "/d/" in url_or_id:
        file_id = url_or_id.split("/d/")[1].split("/")[0]
    
    file_id = file_id.strip()
    base_url = "https://docs.google.com/uc?export=download"

    try:
        print(f"🌐 Fetching from Google Drive ID: {file_id}")
        
        # 2. First attempt to get the file and grab the confirmation cookie
        response = session.get(base_url, params={'id': file_id}, headers=headers, stream=True)
        
        confirm_token = None
        for key, value in response.cookies.items():
            if 'download_warning' in key:
                confirm_token = value
                break
        
        # 3. If Google sent a warning token, request again with 'confirm'
        if confirm_token:
            print("🔑 Bypassing Google scan warning...")
            response = session.get(base_url, params={'id': file_id, 'confirm': confirm_token}, headers=headers, stream=True)

        if response.status_code != 200:
            raise Exception(f"Google Drive returned status {response.status_code}")

        # 4. Load the image from memory
        image_content = response.content
        image = Image.open(BytesIO(image_content))

        # 5. Detect extension and save
        ext = image.format.lower() if image.format else "png"
        if ext == "jpeg": ext = "jpg"
        
        filename = f"{name.replace(' ', '_')}.{ext}"
        path = os.path.join("photos", filename)

        # Convert to RGB if it's a JPEG to avoid transparency issues
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        image.save(path)
        print(f"✅ Photo successfully saved: {path}")
        
        # Return the absolute path for card_generator.py to find it
        return os.path.abspath(path)

    except Exception as e:
        print(f"❌ DOWNLOAD ERROR: {str(e)}")
        # This is what n8n sees
        raise Exception(f"Image Error: {str(e)}")
    

    