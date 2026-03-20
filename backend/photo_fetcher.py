import requests
import os
from PIL import Image


def download_photo(url, name):

    if not os.path.exists("photos"):
        os.makedirs("photos")

    path = f"photos/{name}.jpg"

    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # 🔥 HANDLE GOOGLE DRIVE PROPERLY
        if "drive.google.com" in url:
            if "thumbnail" in url:
                # already correct format
                download_url = url
            else:
                file_id = url.split("id=")[-1]
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

            response = session.get(download_url, headers=headers, stream=True)

            # 🔥 Handle confirmation token (large files)
            for key, value in response.cookies.items():
                if key.startswith("download_warning"):
                    download_url = f"{download_url}&confirm={value}"
                    response = session.get(download_url, headers=headers, stream=True)
                    break
        else:
            response = session.get(url, headers=headers, stream=True)

        # ❌ If request failed
        if response.status_code != 200:
            raise Exception(f"Failed to fetch image. Status: {response.status_code}")

        # 💾 Save file
        with open(path, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)

        # 🔥 CRITICAL: VALIDATE IMAGE
        try:
            img = Image.open(path)
            img.verify()
        except:
            raise Exception("Downloaded file is NOT a valid image (Google returned HTML)")

        print("✅ Photo saved:", path)

    except Exception as e:
        print("❌ ERROR:", e)
        raise e  # 🔥 important: fail fast

    return path

