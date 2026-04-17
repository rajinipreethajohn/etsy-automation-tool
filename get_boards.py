import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

url = "https://api.pinterest.com/v5/boards"

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)