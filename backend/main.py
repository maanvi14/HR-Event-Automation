from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.event_engine import detect_events
import os

app = FastAPI()

# ✅ Ensure folder exists
os.makedirs("generated_cards", exist_ok=True)

# ✅ Serve images
app.mount("/images", StaticFiles(directory="generated_cards"), name="images")


@app.get("/")
def home():
    return {"message": "KSAP HR Automation System Running"}


# 🚨 THIS IS YOUR IMPORTANT ROUTE
@app.get("/run-events")
def run_events():
    events = detect_events()

    return {
        "status": "success",
        "total": len(events),
        "events": events
    }

    