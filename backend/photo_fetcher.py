import requests
import os
from PIL import Image
from io import BytesIO

def download_photo(url_or_id, name):
    os.makedirs("photos", exist_ok=True)
    session = requests.Session()
    # Real-world browser headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # ================= 1. EXTREME ID CLEANING =================
    # This handles full URLs, raw IDs, and messy IDs with extra parameters
    file_id = url_or_id
    if "id=" in url_or_id:
        file_id = url_or_id.split("id=")[-1]
    elif "/d/" in url_or_id:
        file_id = url_or_id.split("/d/")[1].split("/")[0]
    
    # Crucial: Remove anything after &, ?, or / that isn't the ID
    file_id = file_id.split("&")[0].split("?")[0].split("/")[0].strip()
    
    base_url = "https://docs.google.com/uc?export=download"

    try:
        print(f"🌐 Fetching clean ID: {file_id}")
        
        # ================= 2. BYPASS GOOGLE WARNING =================
        response = session.get(base_url, params={'id': file_id}, headers=headers, stream=True)
        
        confirm_token = None
        for key, value in response.cookies.items():
            if 'download_warning' in key:
                confirm_token = value
                break
        
        if confirm_token:
            print("🔑 Found bypass token, requesting again...")
            response = session.get(base_url, params={'id': file_id, 'confirm': confirm_token}, headers=headers, stream=True)

        if response.status_code != 200:
            print(f"❌ GOOGLE ERROR: Status {response.status_code}")
            raise Exception(f"Google Drive returned {response.status_code}. Check file permissions.")

        # ================= 3. VALIDATE CONTENT =================
        content = response.content
        if len(content) < 2000: # Typical error pages are small HTML files
            content_str = content.decode('utf-8', errors='ignore')
            if "Google Drive - Quota exceeded" in content_str:
                raise Exception("Google Drive download quota exceeded for this file.")
            if "Unauthorized" in content_str or "<html" in content_str.lower():
                raise Exception("Link returned HTML instead of an image. Is the file shared with 'Anyone with link'?")

        # ================= 4. PROCESS & SAVE =================
        # Use Image.open to verify it's actually an image
        image = Image.open(BytesIO(content))
        
        ext = image.format.lower() if image.format else "png"
        if ext == "jpeg": ext = "jpg"
        
        filename = f"{name.replace(' ', '_')}.{ext}"
        path = os.path.join("photos", filename)

        # Convert to RGBA for consistency (prevents mode errors in card_generator)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        image.save(path)
        print(f"✅ Photo successfully saved: {path}")
        
        # Return the absolute path
        return os.path.abspath(path)

    except Exception as e:
        print(f"❌ DOWNLOAD FAILED: {str(e)}")
        # Raise a clear error that main.py can catch
        raise Exception(f"Image Error: {str(e)}")
    
    