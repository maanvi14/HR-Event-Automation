from fastapi import FastAPI
from backend.event_engine import detect_events

app = FastAPI()


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