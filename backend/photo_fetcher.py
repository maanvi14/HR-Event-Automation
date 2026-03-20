import requests
import os
from PIL import Image
from io import BytesIO


def download_photo(url, name):

    os.makedirs("photos", exist_ok=True)
    path = f"photos/{name}.png"

    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # ================= GOOGLE DRIVE FIX =================
        if "drive.google.com" in url:
            file_id = url.split("id=")[-1].split("&")[0]
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

        print("🌐 Fetching:", url)

        response = session.get(url, headers=headers, timeout=10)

        print("STATUS:", response.status_code)
        print("TYPE:", response.headers.get("Content-Type"))

        if response.status_code != 200:
            raise Exception("Failed to fetch image")

        # ================= VALIDATE CONTENT =================
        if "image" not in response.headers.get("Content-Type", ""):
            raise Exception("Not an image (HTML or blocked content)")

        # ================= LOAD IMAGE SAFELY =================
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")
        image.save(path, "PNG")

        print("✅ Photo saved:", path)
        return path

    except Exception as e:
        print("❌ ERROR:", e)

        # ================= FALLBACK (CRITICAL 🔥) =================
        fallback_path = "templates/default_user.png"

        if not os.path.exists(fallback_path):
            raise Exception("Fallback image missing. Add templates/default_user.png")

        print("⚠️ Using fallback image")

        return fallback_path