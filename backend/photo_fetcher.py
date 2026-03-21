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
        if "drive.google.com" in url:
            file_id = url.split("id=")[-1].split("&")[0]
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

        print("🌐 Fetching:", url)

        response = session.get(url, headers=headers, timeout=10)

        print("STATUS:", response.status_code)
        content_type = response.headers.get("Content-Type", "")
        print("TYPE:", content_type)

        if response.status_code != 200:
            raise Exception("Failed to fetch image")

        # ❗ STRICT CHECK
        if "image" not in content_type:
            raise Exception("Response is not an image (likely HTML page)")

        # ================= LOAD IMAGE =================
        image = Image.open(BytesIO(response.content))

        # ✅ detect format properly
        ext = image.format.lower() if image.format else "png"

        path = f"photos/{name}.{ext}"

        # convert safely
        if ext in ["jpeg", "jpg"]:
            image = image.convert("RGB")
        else:
            image = image.convert("RGBA")

        image.save(path)

        print("✅ Photo saved:", path)

        return path

    except Exception as e:
        print("❌ ERROR:", e)

        # ================= FALLBACK =================
        fallback_path = "templates/default_user.png"

        if not os.path.exists(fallback_path):
            raise Exception("Fallback image missing. Add templates/default_user.png")

        print("⚠️ Using fallback image")

        return fallback_path