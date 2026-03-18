import requests

def send_gchat(message, image_url=None):

    webhook_url = "https://chat.googleapis.com/v1/spaces/AAQAz9uxeWU/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=-AY9bKBrYHzkowodI2NiacPV0f8UGYVE0H0Zew9ZWGU"

    # ✅ SIMPLE TEXT + IMAGE LINK (BEST METHOD)
    if image_url:
        message = f"{message}\n{image_url}"

    response = requests.post(
        webhook_url,
        json={"text": message}
    )

    if response.status_code == 200:
        print("✅ Message sent to Google Chat")
    else:
        print("❌ Failed:", response.text)