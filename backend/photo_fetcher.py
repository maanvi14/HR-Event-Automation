import requests
import os
from PIL import Image
from io import BytesIO


def download_photo(url, name):

    os.makedirs("photos", exist_ok=True)

    try:
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0"}

        # ================= GOOGLE DRIVE FIX =================
        file_id = None

        # Case 1: Full Google Drive link
        if "drive.google.com" in url:
            if "id=" in url:
                file_id = url.split("id=")[-1].split("&")[0]
            elif "/d/" in url:
                file_id = url.split("/d/")[1].split("/")[0]

        # Case 2: Only file_id passed
        elif len(url.strip()) < 50:
            file_id = url.strip()

        # Convert to direct download link
        if file_id:
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

        print("🌐 Fetching:", url)

        response = session.get(url, headers=headers, timeout=15)

        print("STATUS:", response.status_code)
        content_type = response.headers.get("Content-Type", "")
        print("TYPE:", content_type)

        if response.status_code != 200:
            raise Exception("Failed to fetch image")

        # ❗ STRICT VALIDATION
        if "image" not in content_type:
            raise Exception("Response is not an image (likely HTML or permission issue)")

        # ================= LOAD IMAGE =================
        image = Image.open(BytesIO(response.content))

        # Detect format safely
        ext = image.format.lower() if image.format else "png"

        # Normalize extension
        if ext == "jpeg":
            ext = "jpg"

        path = f"photos/{name}.{ext}"

        # Convert mode safely
        if ext in ["jpg", "jpeg"]:
            image = image.convert("RGB")
        else:
            image = image.convert("RGBA")

        image.save(path)

        print("✅ Photo saved:", path)

        return path

    except Exception as e:
        print("❌ ERROR:", e)
        raise Exception("Image download failed - cannot generate card")
    
    