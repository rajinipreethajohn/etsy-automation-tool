import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")

BOARD_ID = "YOUR_BOARD_ID"

url = "https://api.pinterest.com/v5/pins"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "board_id": BOARD_ID,
    "title": "Mindful Toddler Yoga Cards",
    "description": "Screen-free yoga fun for toddlers. Calm routines, movement and mindfulness.",
    "link": "https://www.etsy.com/shop/MindfulYogiBoutique",
    "media_source": {
        "source_type": "image_url",
        "url": "https://your-image-url.com/image.jpg"
    }
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.text)
