from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from backend.card_generator import generate_card
from backend.photo_fetcher import download_photo
import os

app = FastAPI()

# ✅ Ensure folders exist
os.makedirs("generated_cards", exist_ok=True)
os.makedirs("photos", exist_ok=True)

# ✅ Serve generated images publicly
app.mount("/cards", StaticFiles(directory="generated_cards"), name="cards")


@app.get("/")
def home():
    return {"message": "HR Automation API Running 🚀"}


# 🔥 MAIN API USED BY n8n
@app.post("/generate-card")
async def generate_card_api(request: Request):
    try:
        data = await request.json()

        print("DATA RECEIVED:", data)

        name = data.get("name")
        event_type = data.get("event_type")
        photo_url = data.get("photo_url")

        # ✅ Validate input
        if not name or not event_type or not photo_url:
            return {"error": "Missing required fields"}

        print("Processing:", name, event_type, photo_url)

        # Step 1: Download photo
        photo_path = download_photo(photo_url, name)
        print("Photo path:", photo_path)

        # Step 2: Generate card
        output_path = generate_card(
            name,
            f"Happy {event_type}",
            photo_path,
            event_type
        )
        print("Output path:", output_path)

        # Step 3: Return PUBLIC URL (IMPORTANT 🔥)
        filename = os.path.basename(output_path)

        return {
            "image_url": f"https://hr-event-automation.onrender.com/cards/{filename}"
        }

    except Exception as e:
        print("ERROR OCCURRED:", str(e))
        return {"error": str(e)}
    
    