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
from tts import tts_process, tts_process_file
from stt import transcribe
import requests

def generate_short():
    submissions = get_submissions("askreddit")
    submission = submissions[random.randint(0, len(submissions)-1)]
    # gen_short_title(submission, False)
    comments = submissions[2].comments[:3]
    gen_short_comments(comments, False)
    previous_duration = 0
    #clips = [background.set_duration(previous_duration + thanks_audio.duration), title]
    background_clip = (mp.VideoFileClip("./footage/tunnel.mp4").resize((720, 1280)))
    body_split = comments[0].body.split(" ")
    clips = [background_clip]
    print(body_split, len(body_split))
    for i in range(0, len(body_split)):
        print("text:", body_split[i])
        duration = 1
        txt_clip = (mp.TextClip(body_split[i], fontsize = 75, color = 'white')
            .set_duration(duration)
            .set_start(previous_duration))
        previous_duration += duration
        clips.append(txt_clip)
    #background_audio = mp.vfx.loop(background_audio, duration=(previous_duration + thanks_audio.duration))
    #audio_clips = [background_audio.set_duration(previous_duration + thanks_audio.duration), title_audio, thanks_audio] 
    #audio_clips += audio_comments
    final = mp.CompositeVideoClip(clips)
    
    #new_audioclip = mp.CompositeAudioClip(audio_clips)
    #final.audio = new_audioclip
    final.write_videofile("test.mp4", fps=24)
def gen_short_comments(comments, tts):
    print(len(comments), comments[0])
    if tts:
        tts_process_file(comments[0].body)
        result = transcribe("shorts/test/comments.wav")
        print(result)
def gen_short_title(submission, tts):
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
    image.save("./shorts/test/title.png")
    if tts:
        tts_process(submission.title, "/shorts/test/title.wav")
generate_short()