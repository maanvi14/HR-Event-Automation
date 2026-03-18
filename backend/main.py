from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.event_engine import detect_events

app = FastAPI()

# ✅ Serve generated images (VERY IMPORTANT)
app.mount("/images", StaticFiles(directory="generated_cards"), name="images")


@app.get("/")
def home():
    return {"message": "KSAP HR Automation System Running"}


@app.get("/run-events")
def run_events():
    events = detect_events()   # already handles everything

    return {
        "status": "success",
        "total": len(events),
        "events": events
    }