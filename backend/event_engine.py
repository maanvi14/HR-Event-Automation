import pandas as pd
from datetime import datetime
from backend.photo_fetcher import download_photo
from backend.card_generator import generate_card


def detect_events():

    df = pd.read_csv("data/employees.csv")
    today = datetime.today().strftime("%m-%d")

    generated_events = []   # ✅ FIX: store results

    for _, row in df.iterrows():

        name = row["name"]
        image_url = row.get("photo_link")

        if not image_url:
            print(f"⚠️ Missing photo for {name}")
            continue

        photo_path = download_photo(image_url, name)

        dob = pd.to_datetime(row["dob"]).strftime("%m-%d")
        joining_date = pd.to_datetime(row["joining_date"])

        # 🎂 Birthday
        if dob == today:
            path = generate_card(
                name,
                "Wishing you a very happy birthday and all the best for the coming year.",
                photo_path,
                "birthday"
            )

            generated_events.append({
                "name": name,
                "type": "birthday",
                "card": path
            })

        # 🎉 Anniversary
        if joining_date.strftime("%m-%d") == today:

            years = datetime.today().year - joining_date.year  # 🔥 FIX

            path = generate_card(
                name,
                "Cheers to all your accomplishments and thank you for being such a valuable part of the team.",
                photo_path,
                "anniversary",
                years   # 🔥 PASS YEARS
            )

            generated_events.append({
                "name": name,
                "type": "anniversary",
                "years": years,
                "card": path
            })

    return generated_events   # ✅ IMPORTANT