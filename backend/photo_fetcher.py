import requests
import os


def download_photo(url, name):

    if not os.path.exists("photos"):
        os.makedirs("photos")

    path = f"photos/{name}.jpg"

    try:
        session = requests.Session()

        if "drive.google.com" in url:
            file_id = url.split("id=")[-1]
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

            response = session.get(download_url, stream=True)

            # handle large file confirmation token
            for key, value in response.cookies.items():
                if key.startswith("download_warning"):
                    download_url = f"{download_url}&confirm={value}"
                    response = session.get(download_url, stream=True)
                    break
        else:
            response = session.get(url, stream=True)

        # save file
        with open(path, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)

        print("✅ Photo saved:", path)

    except Exception as e:
        print("❌ Download failed:", e)

    return path
