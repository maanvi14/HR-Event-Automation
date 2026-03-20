from fastapi import FastAPI
from fastapi.responses import FileResponse
from backend.card_generator import generate_card
from backend.photo_fetcher import download_photo
import os

app = FastAPI()

# Ensure folders exist (for temporary usage)
os.makedirs("generated_cards", exist_ok=True)
os.makedirs("photos", exist_ok=True)


@app.get("/")
def home():
    return {"message": "HR Automation API Running 🚀"}


# 🔥 MAIN API USED BY n8n
@app.post("/generate-card")
def generate_card_api(data: dict):
    name = data.get("name")
    event_type = data.get("event_type")
    photo_url = data.get("photo_url")

    # Step 1: Download photo
    photo_path = download_photo(photo_url, name)

    # Step 2: Generate card
    output_path = generate_card(
        name,
        f"Happy {event_type}",
        photo_path,
        event_type
    )

    # ✅ IMPORTANT: Return image directly (no storage dependency)
    return FileResponse(output_path, media_type="image/png")

