import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"

API_KEY = os.getenv("STEAM_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing STEAM_API_KEY")

OUTPUT = Path("data")
OUTPUT.mkdir(exist_ok=True)

for file in OUTPUT.glob("*.json"):
    file.unlink()

last_appid = 0
page = 1

while True:
    response = requests.get(
        url,
        headers={"x-webapi-key": API_KEY},
        params={
            "include_games": True,
            "include_dlc": True,
            "include_software": True,
            "include_videos": True,
            "include_hardware": True,
            "max_results": 50000,
            "last_appid": last_appid,
        },
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()["response"]

    apps = [
        {
            "appid": app["appid"],
            "name": app["name"],
        }
        for app in data["apps"]
    ]

    with open(OUTPUT / f"steam_apps_{page:03}.json", "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=4)

    last_appid = data["last_appid"]

    if last_appid == 0:
        break

    page += 1