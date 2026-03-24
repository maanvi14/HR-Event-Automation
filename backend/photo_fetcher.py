import requests
import os
from PIL import Image
from io import BytesIO


def download_photo(url, name):
    os.makedirs("photos", exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        print(f"🌐 Fetching Image: {url}")

        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch image: {response.status_code}")

        content = response.content

        # Validate (avoid HTML error pages)
        if b"<html" in content.lower():
            raise Exception("Invalid image URL (received HTML instead of image)")

        # Normalize image (prevents format issues)
        image = Image.open(BytesIO(content)).convert("RGB")

        filename = f"{name.replace(' ', '_')}.png"
        path = os.path.abspath(os.path.join("photos", filename))

        image.save(path, "PNG")

        print(f"✅ Photo Saved: {path}")

        return path

    except Exception as e:
        raise Exception(f"Download Error: {str(e)}")
    

    