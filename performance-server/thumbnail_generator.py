from PIL import Image, ImageFont, ImageDraw

import os
import util

def GenerateThumbnail(id, genre, title):
    path = os.path.join("scripts", id, "thumbnail.png")
    icon = Image.open("content/data-science.png").convert("RGBA")
    img = Image.new('RGB', (1920, 1080), (47, 47, 47))
    d = ImageDraw.Draw(img)
    textwrap = util.textwrap(title, 10)
    if len(textwrap) == 1:
        fontsize = 150
    elif len(textwrap) == 2:
        fontsize = 125
    elif len(textwrap) == 3:
        fontsize = 100
    elif len(textwrap) == 4:
        fontsize = 90
    else:
        fontsize = 75
    fnt = ImageFont.truetype("fonts/Roboto-Bold.ttf", fontsize)
    text = "\n".join(textwrap).upper()
    size = (d.multiline_textbbox(
        xy=(0, 0),
        text=text,
        font=fnt
    ))
    center = util.GetCenter(1920, 1080, size[2], size[3])
    d.multiline_text((center[0]-250, center[1]), text=text, font=fnt, fill=(255, 255, 255), align="left")
    img.paste(icon, (1300, 250), icon)
    img.save(path)
