import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.card_generator import generate_card
from backend.photo_fetcher import download_photo

app = FastAPI()

# ================= PATH SETUP (Render-safe) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# If main.py is in root, PROJECT_ROOT is BASE_DIR. 
# If main.py is in /backend, use os.path.join(BASE_DIR, "..")
PROJECT_ROOT = BASE_DIR 

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
        name = data.name.strip()
        event_type = data.event_type.lower().strip()
        
        print(f"📥 Received Request: {name} ({event_type})")

        # 1. Download & Process Photo
        photo_path = download_photo(data.photo_url, name)
        
        # 2. Set Custom Message
        if event_type == "birthday":
            message = "Wishing you a day filled with happiness and a year filled with joy!"
        else:
            message = "Congratulations on reaching this wonderful milestone!"
        
        # 3. Generate the Card
        output_path = generate_card(
            name=name,
            message=message,
            photo_path=photo_path,
            event_type=event_type
        )

        # 4. Build Public URL (Update this to your actual Render URL)
        filename = os.path.basename(output_path)
        image_url = f"https://hr-event-automation.onrender.com/cards/{filename}"

        return {"status": "success", "image_url": image_url}

    except Exception as e:
        print(f"❌ API ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    
    