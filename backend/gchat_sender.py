import requests


def send_to_gchat(webhook_url, text):

    data = {
        "text": text
    }

    requests.post(webhook_url, json=data)