import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.card_generator import generate_card
from backend.photo_fetcher import download_photo

app = FastAPI()

# ================= PATH SETUP (Render-safe) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Move up one level to ensure folders are in the project root
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

CARDS_DIR = os.path.join(PROJECT_ROOT, "generated_cards")
PHOTOS_DIR = os.path.join(PROJECT_ROOT, "photos")

os.makedirs(CARDS_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)

# ================= STATIC FILE SERVING =================
app.mount("/cards", StaticFiles(directory=CARDS_DIR), name="cards")

@app.get("/")
def home():
    return {"message": "HR Automation API is Online 🚀"}

class CardRequest(BaseModel):
    name: str
    event_type: str
    photo_url: str

@app.post("/generate-card")
async def generate_card_api(data: CardRequest):
    try:
        print(f"📥 Received Request: {data.name} ({data.event_type})")

        # 1. Download & Process Photo
        # Returns absolute path to the saved image
        photo_path = download_photo(data.photo_url, data.name)
        
        # 2. Generate the Card
        # You can customize the message logic here
        message = f"Wishing you a wonderful {data.event_type.lower()}!"
        
        output_path = generate_card(
            name=data.name,
            message=message,
            photo_path=photo_path,
            event_type=data.event_type
        )

        # 3. Build Public URL
        filename = os.path.basename(output_path)
        image_url = f"https://hr-event-automation.onrender.com/cards/{filename}"

        return {
            "status": "success",
            "image_url": image_url
        }

    except Exception as e:
        print(f"❌ API ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}