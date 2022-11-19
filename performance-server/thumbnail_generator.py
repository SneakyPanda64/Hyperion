import random

from PIL import Image, ImageFont, ImageDraw
import json
import os
import util

import re

from bs4 import BeautifulSoup

import util
import logging
import requests
def GenerateThumbnail(id):
    path = os.path.join(os.path.curdir, "scripts", id)
    j = json.load(open(os.path.join(path, "script.json")))
    SearchIcons(j["topic"])
    icon = Image.open(os.path.join(os.path.curdir, "content", "thumbnail-icon.png")).convert("RGBA")
    img = Image.open(os.path.join(os.path.curdir, "content", "thumbnail.png")) # Image.new('RGB', (1920, 1080), (47, 47, 47))
    d = ImageDraw.Draw(img)
    textwrap = util.textwrap(j["topic"], 15)
    fontsize = 65
    fnt = ImageFont.truetype("fonts/Roboto-Bold.ttf", fontsize)
    text = "\n".join(textwrap)
    d.multiline_text((75, 25), text=text, font=fnt, fill=(68, 68, 68), align="left")
    img.paste(icon, (500, 250), icon)
    img.save(os.path.join(path, "thumbnail.png"))
    return True
def SearchIcons(query):
    keywords = util.complete(
        prompt=f"Extract keywords from the following sentences:\n\n{query}\n\nkeywords:",
        model="text-babbage-001",
        temperature=0
    ).choices[0].text.strip().split(",")
    keywords = [x for x in keywords if x]
    image = ""
    for keyword in keywords:
        image = GetIcon(keyword)
        if image != False:
            break
    logging.debug(image)
    img_data = requests.get(image).content
    with open(os.path.join(os.path.curdir, "content", "thumbnail-icon.png"), 'wb') as handler:
        handler.write(img_data)
def GetIcon(keyword):
    logging.debug("Getting requests for icons")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(f"https://www.flaticon.com/search?word={keyword}&color=color&shape=outline&order_by=4", headers=headers)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        icons = int((soup.find('p', id="total_icon_badge").string).replace(",", ""))
        upper_bound = 96
        if icons < 96:
            upper_bound = icons
        images = ([v["data-src"].replace("com/128", "com/256") for v in soup.findAll('img')[10:upper_bound]]) #  if re.search("^http.*\/hello$", v)
        return random.choice(images[:10])
    else:
        return False
    #VideosFromJSON(path, response.json())