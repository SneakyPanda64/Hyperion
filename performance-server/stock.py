import urllib.request
import requests
import os
import time as time
import util
import shutil
from tqdm.auto import tqdm
import logging

def GetFootage(path, query, quantity):
    headers = {
        'Authorization': os.getenv("PEXELS_API_KEY"),
    }
    params = {
        'query': query,
        'per_page': quantity,
        "size": "medium",
        "orientation": "landscape"
    }
    logging.debug("Getting requests for stock footage")
    response = requests.get('https://api.pexels.com/videos/search', params=params, headers=headers)
    VideosFromJSON(path, response.json())
def VideosFromJSON(path, j):
    for v in j["videos"]:
        link = ""
        for b in v["video_files"]:
            link = b["link"]
            if b["quality"] == "hd" and b["width"] >= 1920:
                break
        GetVideoFromURL(path, link)
def GetVideoFromURL(path, url):
    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
            with open(os.path.join(path, f"{int(time.time()*1000)}.mp4"), "wb") as output:
                shutil.copyfileobj(raw, output)