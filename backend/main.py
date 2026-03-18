from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.event_engine import detect_events
import os

app = FastAPI()

# ✅ IMPORTANT FIX (ADD THIS)
if not os.path.exists("generated_cards"):
    os.makedirs("generated_cards")

# ✅ Serve images
app.mount("/images", StaticFiles(directory="generated_cards"), name="images")


@app.get("/")
def home():
    return {"message": "KSAP HR Automation System Running"}


@app.get("/run-events")
def run_events():
    events = detect_events()

    return {
        "status": "success",
        "total": len(events),
        "events": events
    }

