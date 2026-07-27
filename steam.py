import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.steampowered.com/IStoreService/GetAppList/v1/"

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
        URL,
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

    result = response.json()

    if "response" not in result:
        raise RuntimeError(f"Unexpected response: {result}")

    data = result["response"]

    apps = [
        {
            "appid": app["appid"],
            "name": app["name"],
        }
        for app in data.get("apps", [])
    ]

    with open(
        OUTPUT / f"steam_apps_{page:03}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            apps,
            f,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Page {page}: {len(apps)} apps")

    next_appid = data.get("last_appid")

    if not next_appid or next_appid == last_appid:
        break

    last_appid = next_appid
    page += 1

print("Done.")