import smtplib
from email.mime.text import MIMEText


def send_email(receiver, subject, message):

    sender = "your_email@gmail.com"
    password = "your_password"

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    server.login(sender, password)

    server.sendmail(sender, receiver, msg.as_string())

    server.quit()