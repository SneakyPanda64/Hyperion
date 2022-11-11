import urllib.request
import requests
import os
import time as time
import util
import shutil
from tqdm.auto import tqdm

def SearchVideos(id, query, quantity):
    headers = {
        'Authorization': '563492ad6f91700001000001dee3131100234da996205fe67eaa5cbb',
    }
    params = {
        'query': query,
        'per_page': quantity,
        "size": "medium",
        "orientation": "landscape"
    }
    response = requests.get('https://api.pexels.com/videos/search', params=params, headers=headers)
    VideosFromJSON(id, response.json())
def VideosFromJSON(id, j):
    for v in j["videos"]:
        link = ""
        for b in v["video_files"]:
            link = b["link"]
            if b["quality"] == "hd" and b["width"] >= 1920:
                break
        GetVideoFromURL(id, link)
def GetVideoFromURL(id, url):
    path = os.path.join("scripts", id, "videos")
    print(f"Downloading stock footage from {url}")
    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
            with open(os.path.join(path, f"{int(time.time()*1000)}.mp4"), "wb") as output:
                shutil.copyfileobj(raw, output)