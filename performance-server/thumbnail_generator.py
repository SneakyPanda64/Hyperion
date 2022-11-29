import random
import shutil
import keyphrase

from PIL import Image, ImageFont, ImageDraw, ImageColor
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
    keyphrases = GetKeyphrases(" ".join(j["passages"]))
    print(keyphrases)
    SearchIcons(keyphrases)
    if " vs" in j["topic"]:
        img = Versus(j["topic"])
    else:
        img = Orginal(j["topic"])
    img.save(os.path.join(path, "thumbnail.png"))
    return True
def GetKeyphrases(text):
    model_name = "ml6team/keyphrase-generation-t5-small-inspec"
    generator = keyphrase.KeyphraseGenerationPipeline(model=model_name)
    return generator(text)
def Circles(background):
    img = Image.new('RGBA', (1920, 1080), (255, 255, 255))
    dimensions = [
        (50, 650, 550, "#bcefde",
            (100, 750, 400, "#a1e9d0")
        ), (1350, 650, 550, "#bcefde",
            (1450, 750, 400, "#a1e9d0")
        ), (1425, 0, 400, "#bcefde",
            (1525, 0, 300, "#a1e9d0")
        )
    ]
    for v in random.choices(dimensions, k=2):
        x, y, size, colour, opacity = v
        size = random.randint(round(size * 0.8), size)
        img = DrawCircle(img, x, y, size, ImageColor.getcolor(colour, "RGBA"))
        if random.randint(0, 2) == 1:
            x, y, size, colour = opacity
            img = DrawCircle(img, x, y, size, ImageColor.getcolor(colour, "RGBA"))
    img = img.crop((320, 180, 1600, 900))
    background.paste(img, (0, 0), img)
    return background
def DrawCircle(img, x, y, size, colour):
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse(
        (x, y, size + x, size + y),
        fill=colour)
    return img
def Base(title):
    # img = Image.open(
    #     os.path.join(os.path.curdir, "content", "thumbnail.png"))
    img = Image.new('RGB', (1280, 720), (255, 255, 255))
    img = Circles(img)
    d = ImageDraw.Draw(img)
    d.rectangle([(40, 20), (100, 80)], fill=ImageColor.getcolor("#bcefde", "RGBA"))
    textwrap = util.textwrap(title, 15)
    fnt = ImageFont.truetype("fonts/Roboto-Bold.ttf", 65)
    text = "\n".join(textwrap)
    d.multiline_text((65, 25), text=text, font=fnt, fill=(68, 68, 68), align="left")
    return img
def Orginal(title):
    img = Base(title)
    path = os.path.join("content", "thumbnail-icons")
    icon = Image.open(os.path.join(path, random.choice(os.listdir(path)))).convert("RGBA")
    img.paste(icon, (500, 250), icon)
    return img
def Versus(title):
    img = Base(title)
    path = os.path.join("content", "thumbnail-icons")
    icon1 = Image.open(os.path.join(path, random.choice(os.listdir(path)))).convert("RGBA")
    icon2= Image.open(os.path.join(path, random.choice(os.listdir(path)))).convert("RGBA")
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("fonts/Roboto-Bold.ttf", 120)
    d.text((540, 300), "VS", font=fnt, fill=(68, 68, 68))
    img.paste(icon1, (200, 250), icon1)
    img.paste(icon2, (800, 250), icon2)
    return img
def SearchIcons(keywords):
    keywords = [x for x in keywords if x]
    images = []
    for keyword in keywords:
        images = GetIcon(keyword)
        if images != False:
            break
    logging.debug(images)
    path = os.path.join(os.path.curdir, "content", "thumbnail-icons")
    try:
        shutil.rmtree(path)
    except:
        pass
    os.mkdir(path)
    for i, image in enumerate(images):
        img_data = requests.get(image).content
        with open(os.path.join(path, f"{i}.png"), 'wb') as handler:
            handler.write(img_data)
def GetIcon(keywords):
    logging.debug("Getting requests for icons")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    images = []
    for keyword in keywords:
        response = requests.get(f"https://www.flaticon.com/search?word={keyword}&color=color&shape=outline&order_by=4", headers=headers)
        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, "html.parser")
            icons = int((soup.find('p', id="total_icon_badge").string).replace(",", ""))
            upper_bound = 96
            if icons < 96:
                upper_bound = icons
            images += ([v["data-src"].replace("com/128", "com/256") for v in soup.findAll('img')[10:upper_bound+10]])[:5] #  if re.search("^http.*\/hello$", v)
    if len(images) < 1:
        return False
    return images
    #VideosFromJSON(path, response.json())