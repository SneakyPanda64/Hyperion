from asyncio import futures
import mutagen
from mutagen.wave import WAVE
import moviepy.editor as mp
import os
from PIL import Image, ImageFont, ImageDraw, ImageChops, ImageOps
import textwrap
import numpy as np
from reddit import get_comments, get_submissions
import random
from tts import tts_process
import requests

def generate_video(size, overwrite, tts):
    if overwrite: 
        if tts:
            clear_files("audio")
        clear_files("images")
        submissions = get_submissions("askreddit")
        submission = submissions[random.randint(0, len(submissions)-1)]
        gen_title(submission, tts)
        comments = get_comments(submission)
        for i in range(0, size):
            gen_comment(comments[i], str(i), 0, tts)
            # print(i, "comment size", str(comments[i].body.split(" ")))
            if len(comments[i].body.split(" ")) < 50:
                try:
                    # print(i, "reply size", str(len(" ".split(comments[i].replies[0].body))))
                    if len(comments[i].replies[0].body.split(" ")) < 50:
                        gen_comment(comments[i].replies[0], str(i), 1, tts)
                except:
                    print("Failed to extract comment reply body")
    background = mp.ImageClip("./images/background.png")
    #background = mp.VideoFileClip("./footage/tunnel.mp4").resize(width=1920, height=1080)
    background_audio = mp.AudioFileClip("./footage/background.mp3").fx(mp.afx.volumex, 0.025)
    title_duration = WAVE("./results/audio/title.wav").info.length
    title = (mp.ImageClip("./results/images/title.png")
          .set_duration(title_duration)
          .set_pos((400, 350)))
    title_audio = (mp.AudioFileClip("./results/audio/title.wav")
        .set_start(0))
    comments = []
    audio_comments = []
    previous_duration = title_duration
    for i in range(0, size):
        subindex = 0
        # duration = length = WAVE("./results/audio/comments/" + str(i) + "-0.wav").info.length
        if os.path.exists("./results/audio/comments/" + str(i) + "-1.wav"):
            subindex = 1
            # duration += WAVE("./results/audio/comments/" + str(i) + "-1.wav").info.length
        # duration = length
        # if subindex > 0:
        #     duration += WAVE("./results/audio/comments/" + str(i) + "-1.wav").info.length
        
        for j in range(0, subindex+1):
            duration = 0
            future_length = 0
            
            length = WAVE("./results/audio/comments/" + str(i) + "-" + str(j) + ".wav").info.length
            path = "./results/audio/comments/" + str(i) + "-" + str(j) + ".wav"
            print("Previous:", previous_duration, "Length:", length)
            audio = (mp.AudioFileClip(path)
                .set_start(previous_duration))
            if j == 0 and subindex > 0:
                future_length = WAVE("./results/audio/comments/" + str(i) + "-" + str(subindex) + ".wav").info.length + audio.duration
            else:
                future_length = audio.duration
            duration += future_length
            offset_y = 60
            print(duration)
            if j > 0:
                try:
                    with Image.open("./results/images/comments/" + str(i) + "-" + str(j-1) + ".png") as im:
                        width, height = im.size
                        offset_y = offset_y + height
                except:
                    print("Error occured")
            print("Y-Offset", offset_y)
            comment = (mp.ImageClip("./results/images/comments/" + str(i) + "-" + str(j) + ".png")
                    .set_duration(duration)
                    .set_start(previous_duration)
                    .resize(width=1800-(j*50))
                    .set_pos((60+(j*50), offset_y)))
            # print(subindex*(comment.w))
            audio_comments.append(audio)
            comments.append(comment)
            previous_duration += length
        if tts:
            tts_process("Thank you for watching and don't forget to like and subscribe.", "results/audio/thanks.wav")
    thanks_audio = (mp.AudioFileClip("./results/audio/thanks.wav")
        .set_start(previous_duration))
    clips = [background.set_duration(previous_duration + thanks_audio.duration), title]
    clips += comments
    background_audio = mp.vfx.loop(background_audio, duration=(previous_duration + thanks_audio.duration))
    audio_clips = [background_audio.set_duration(previous_duration + thanks_audio.duration), title_audio, thanks_audio] 
    audio_clips += audio_comments
    final = mp.CompositeVideoClip(clips)
    new_audioclip = mp.CompositeAudioClip(audio_clips)
    final.audio = new_audioclip
    final.write_videofile("test.mp4", fps=24)

def gen_title(submission, tts):
    text = submission.title
    wrap_text_length = len(textwrap.wrap(text, width=46))
    wrap_text = textwrap.wrap(text, width=46+((wrap_text_length-1)*3))
    comments = str(len(submission.comments))
    upvotes = "{:.1f}k".format(submission.score/1000)
    if (submission.score/1000 > 99):
        upvotes = str(round(submission.score/1000)) + "k"
    if (submission.score/1000 < 1):
        upvotes = str(submission.score)
    user = submission.author.name
    image = Image.open("./images/reddit_title.png")
    main_font = ImageFont.truetype(font='fonts/Roboto/Roboto-Medium.ttf', size=52-((len(wrap_text)-1)*8))
    comments_font = ImageFont.truetype(font='fonts/Roboto/Roboto-Bold.ttf', size=32)
    upvotes_font = ImageFont.truetype(font='fonts/Roboto/Roboto-Bold.ttf', size=38)
    user_font = ImageFont.truetype(font='fonts/Roboto/Roboto-Regular.ttf', size=26)
    editable = ImageDraw.Draw(image)
    for i, v in enumerate(wrap_text):
        editable.text((145,40+(i+1)*40), v, (255, 255, 255), font=main_font)
    editable.text((215, 222), comments, (126, 131, 132), font=comments_font)
    editable.text((18, 95), upvotes, (209, 209, 209), font=upvotes_font)
    editable.text((145, 30), "Posted by u/" + user, (209, 209, 209), font=user_font)
    image.save("./results/images/title.png")
    if tts:
        tts_process(submission.title, "results/audio/title.wav")
def gen_comment(comment, index, subindex, tts):
    print("[Editor] Generating comment index:", str(index) + "-" + str(subindex))
    author = comment.author.name
    text = str(comment.body) 
    body_font = ImageFont.truetype(font="fonts/Roboto/Roboto-Regular.ttf", size=40)
    author_font = ImageFont.truetype(font="fonts/Roboto/Roboto-Regular.ttf", size=34)
    time_font = ImageFont.truetype(font="fonts/Roboto/Roboto-Regular.ttf", size=30)
    body_text = textwrap.wrap(text, width=100-(subindex*10))
    y = body_font.getsize("\n".join(body_text))[1]
    img = Image.new("RGB", (1920-(subindex*50), (y*(len(body_text))+150)), color=(25, 25, 26))
    editable = ImageDraw.Draw(img)
    editable.text((120, 35), author, (255, 255, 255), font=author_font)
    editable.text((author_font.getsize(author)[0]+130, 40), unix_converter(comment.created_utc), (126, 131, 132), font=time_font)
    for i, v in enumerate(body_text):
        editable.text((50, (40+(i+1)*55)), v, (209, 209, 209), font=body_font)
    try:
        profile_img = crop_image(Image.open(requests.get(comment.author.icon_img, stream=True).raw))
        img.paste(profile_img["image"], (40, 20), profile_img["mask"])
    except:
        print("Could not convert profile")
    img.save("./results/images/comments/" + str(index) + "-" + str(subindex) + ".png")
    if tts:
        try:
            tts_process(comment.body, "results/audio/comments/" + str(index) + "-" + str(subindex) + ".wav")
        except:
            print("[Editor] Comment failed retrying..", str(index) + "-" + str(subindex))
            gen_comment(comment, index, subindex, tts)
def clear_files(type):
    directory = os.path.join(os.path.dirname(__file__), "results", type, "comments")
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            os.remove(f)
def unix_converter(unix):
    unix = unix/1000
    time = str(round(unix/86400)) + " days ago"
    if unix/3600 <= 23:
        time = str(round(unix/3600)) + " hours ago"
    return time
def crop_image(im):
    size = (64, 64)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    return {"image": output, "mask": mask}
def gen_thumbnail():
    img = Image.new("RGB", (1280, 720), color=(0, 0, 0))
    
    # fonts
    subreddit_font = ImageFont.truetype(font='fonts/Roboto/Roboto-Bold.ttf', size=64)
    main_font = ImageFont.truetype(font='fonts/Roboto/Roboto-Regular.ttf', size=110)
    # editable
    editable = ImageDraw.Draw(img)
    wrap_text = textwrap.wrap(width=12, text="What Did You Find Out About Your Friends Personal Life?")
    editable.text((50, 0), "r/AskReddit", (255, 255, 255),font=subreddit_font)
    for i in range(0, len(wrap_text)):
        editable.text((50, 100+(i*90)), wrap_text[i], (255, 255, 255),font=main_font,spacing=0)
    img.save("./results/images/thumbnail.png")
gen_thumbnail()