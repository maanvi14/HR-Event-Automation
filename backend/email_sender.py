import os
from dotenv import load_dotenv

# 🔥 FORCE LOAD ENV FROM ROOT
load_dotenv(dotenv_path=".env")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


def send_email(receiver, subject, message, image_path):

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    print("DEBUG:", sender, password)  # 👈 TEMP DEBUG

    if not sender or not password:
        raise Exception("❌ EMAIL_USER or EMAIL_PASS not set")

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText(message, "plain"))

    with open(image_path, "rb") as img:
        mime_img = MIMEImage(img.read())
        mime_img.add_header("Content-Disposition", "attachment", filename="card.png")
        msg.attach(mime_img)

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

    print("📩 Email sent successfully!")