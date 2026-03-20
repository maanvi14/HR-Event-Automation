from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from backend.card_generator import generate_card
from backend.photo_fetcher import download_photo
import os

app = FastAPI()

# ✅ Ensure folders exist (Render-safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "..", "generated_cards")
PHOTOS_DIR = os.path.join(BASE_DIR, "..", "photos")

os.makedirs(CARDS_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)

# ✅ Serve generated images publicly
app.mount("/cards", StaticFiles(directory=CARDS_DIR), name="cards")


@app.get("/")
def home():
    return {"message": "HR Automation API Running 🚀"}


# 🔥 MAIN API USED BY n8n
@app.post("/generate-card")
async def generate_card_api(request: Request):
    try:
        data = await request.json()

        print("📥 DATA RECEIVED:", data)

        name = data.get("name")
        event_type = data.get("event_type")
        photo_url = data.get("photo_url")

        # ✅ Validate input
        if not name or not event_type or not photo_url:
            return {"error": "Missing required fields"}

        print("⚙️ Processing:", name, event_type)

        # Step 1: Download photo
        photo_path = download_photo(photo_url, name)
        print("🖼️ Photo path:", photo_path)

        # Step 2: Generate card
        output_path = generate_card(
            name,
            f"Happy {event_type}",
            photo_path,
            event_type
        )
        print("🎉 Card generated:", output_path)

        # Step 3: Return PUBLIC URL
        filename = os.path.basename(output_path)

        image_url = f"https://hr-event-automation.onrender.com/cards/{filename}"

        print("🌐 Public URL:", image_url)

        return {
            "status": "success",
            "image_url": image_url
        }

    except Exception as e:
        print("❌ ERROR OCCURRED:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }
    
    