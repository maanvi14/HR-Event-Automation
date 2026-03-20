from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.card_generator import generate_card
from backend.photo_fetcher import download_photo
import os

app = FastAPI()

# ================= PATH SETUP (Render-safe) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARDS_DIR = os.path.join(BASE_DIR, "..", "generated_cards")
PHOTOS_DIR = os.path.join(BASE_DIR, "..", "photos")

os.makedirs(CARDS_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)

# ================= STATIC FILE SERVING =================
app.mount("/cards", StaticFiles(directory=CARDS_DIR), name="cards")


@app.get("/")
def home():
    return {"message": "HR Automation API Running 🚀"}


# ================= REQUEST MODEL (IMPORTANT 🔥) =================
class CardRequest(BaseModel):
    name: str
    event_type: str
    photo_url: str


# ================= MAIN API =================
@app.post("/generate-card")
async def generate_card_api(data: CardRequest):
    try:
        print("📥 DATA RECEIVED:", data)

        name = data.name
        event_type = data.event_type.lower().strip()
        photo_url = data.photo_url

        # ✅ Validation
        if not name or not event_type or not photo_url:
            return {"status": "error", "message": "Missing required fields"}

        print("⚙️ Processing:", name, event_type)

        # ================= STEP 1: DOWNLOAD =================
        print("⬇️ Downloading image...")
        photo_path = download_photo(photo_url, name)
        print("🖼️ Photo saved at:", photo_path)

        # ================= STEP 2: GENERATE CARD =================
        print("🎨 Generating card...")
        output_path = generate_card(
            name,
            f"Happy {event_type}",
            photo_path,
            event_type
        )
        print("🎉 Card generated at:", output_path)

        # ================= STEP 3: RETURN URL =================
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
    
    