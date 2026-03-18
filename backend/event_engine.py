import pandas as pd
from datetime import datetime
from backend.photo_fetcher import download_photo
from backend.card_generator import generate_card
from backend.email_sender import send_email
from backend.gchat_sender import send_gchat


def detect_events():

    df = pd.read_csv("data/employees.csv")
    today = datetime.today().strftime("%m-%d")

    generated_events = []

    # ✅ YOUR NGROK URL (ADD THIS ONCE)
    BASE_URL = "https://unemitted-irritatedly-bernita.ngrok-free.dev"

    for _, row in df.iterrows():

        name = row["name"]
        email = row.get("email")
        image_url = row.get("photo_link")

        if not image_url:
            print(f"⚠️ Missing photo for {name}")
            continue

        if not email:
            print(f"⚠️ Missing email for {name}")
            continue

        photo_path = download_photo(image_url, name)

        dob = pd.to_datetime(row["dob"]).strftime("%m-%d")
        joining_date = pd.to_datetime(row["joining_date"])

        # 🎂 ================= BIRTHDAY =================
        if dob == today:

            path = generate_card(
                name,
                "Wishing you a very happy birthday and all the best for the coming year.",
                photo_path,
                "birthday"
            )

            if path:
                send_email(
                    email,
                    f"Happy Birthday {name}! 🎂",
                    f"Dear {name},\n\nWishing you a wonderful birthday!\n\nBest,\nTeam",
                    path
                )

                # ✅ ADD THIS (IMPORTANT 🔥)
                filename = path.split("\\")[-1]
                public_url = f"{BASE_URL}/images/{filename}"

                # 💬 Send to Google Chat WITH IMAGE
                send_gchat(f"🎂 Happy Birthday {name}! 🎉", public_url)

            generated_events.append({
                "name": name,
                "type": "birthday",
                "card": path
            })

        # 🎉 ================= ANNIVERSARY =================
        if joining_date.strftime("%m-%d") == today:

            years = datetime.today().year - joining_date.year

            path = generate_card(
                name,
                "Cheers to all your accomplishments and thank you for being such a valuable part of the team.",
                photo_path,
                "anniversary",
                years
            )

            if path:
                send_email(
                    email,
                    f"Happy Work Anniversary {name}! 🎉",
                    f"Dear {name},\n\nCongratulations on {years} years with us!\n\nBest,\nTeam",
                    path
                )

                # ✅ ADD THIS (IMPORTANT 🔥)
                filename = path.split("\\")[-1]
                public_url = f"{BASE_URL}/images/{filename}"

                # 💬 Send to Google Chat WITH IMAGE
                send_gchat(f"🎉 Happy {years} Year Work Anniversary {name}! 🏆", public_url)

            generated_events.append({
                "name": name,
                "type": "anniversary",
                "years": years,
                "card": path
            })

    return generated_events