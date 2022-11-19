import stock
import random
import moviepy.editor as mp
import numpy as np
import os
import json
from PIL import Image
import util
import thumbnail_generator as thumbnail
import logging

def CreateVideo(id):
    path = os.path.join(os.path.curdir, "scripts", id)
    with open(os.path.join(path, "script.json"), "r") as f:
        contents = json.loads(f.read())
    start_time = 3
    full_duration = (mp.AudioFileClip(os.path.join(path, "audio", "audio.wav"))).duration + start_time
    clips = [(mp.VideoFileClip(os.path.join(os.path.curdir, "content", "intro.mp4")).set_duration(3))]
    clips += CreateStockClips(id, start_time, full_duration)
    audio_clips = []
    timeline = []
    for i, v in enumerate(contents["subTopics"]):
        duration = (mp.AudioFileClip(os.path.join(path, "audio", f"audio-{i*2}.wav"))).duration
        passage_duration = (mp.AudioFileClip(os.path.join(path, "audio", f"audio-{(i*2)+1}.wav"))).duration
        section = CreateSectionText(id, i, v, start_time, duration, full_duration)
        audio = CreateSectionAudio(id, i, start_time)
        clips += section
        audio_clips += audio
        timeline.append(start_time)
        start_time += duration + passage_duration

    with open(os.path.join(path, "script.json"), "w") as f:
        contents["timeline"] = timeline
        json.dump(contents, f)
    intro_audio = clips[0].audio
    audio_clips.append(intro_audio.set_duration(3))
    new_audioclip = mp.CompositeAudioClip(audio_clips)
    final = mp.CompositeVideoClip(clips)
    final.audio = new_audioclip
    final.write_videofile(os.path.join(path, "video.mp4"),
                          fps=25)
    final.close()
    return True
def CreateSectionSubtitles(id, index, global_start_time, cap):
    transcription = util.transcribe(os.path.join(os.path.curdir, "scripts", id, "audio", f"audio-{(index * 2) + 1}.wav"))
    clips = []
    for text in transcription["text"]:
        print(text)
        start_time = text["start"] + global_start_time
        end_time = text["end"] + global_start_time
        print(start_time, end_time, cap)
        if end_time > cap:
            end_time = cap
        duration = end_time - start_time
        txt_clip = (mp.TextClip(
            txt="\n".join(util.textwrap(text["text"], 38)),
             font="Roboto-Bold",
             fontsize=55,
             color="rgb(255, 255, 255)",
             align="center"
        ).set_start(start_time).set_duration(duration))
        x = GetXCenter(txt_clip, 1920)
        w, h = txt_clip.size
        txt_clip = txt_clip.set_pos((x, (1080-h)-50))
        clips.append(mp.ColorClip(size=[w+30, h+30], color=np.array([0, 0, 0]).astype(np.uint8)).set_start(start_time).set_duration(duration).set_opacity(0.5).set_pos((x-15, ((1080-h)-50)-15)))
        clips.append(txt_clip)
    return clips
def CreateSectionAudio(id, index, start_time):
    path = os.path.join(os.path.curdir, "scripts", id, "audio")
    audio_clips = []
    topic_audio = (mp.AudioFileClip(os.path.join(path, f"audio-{index*2}.wav"))).set_start(start_time)
    passage_audio = (mp.AudioFileClip(os.path.join(path, f"audio-{(index*2)+1}.wav"))).set_start(start_time + topic_audio.duration)
    audio_clips.append(topic_audio)
    audio_clips.append(passage_audio)
    return audio_clips
def CreateSectionText(id, index, subtopic, start_time, duration, cap):
    txt_clips = []
    textwrapped = util.textwrap(subtopic, 18)
    txt_clip = (mp.TextClip(
        txt="\n".join(textwrapped).upper(),
        font="Roboto-Black",
        stroke_width=3,
        stroke_color="white",
        fontsize=72,
        color="rgb(255, 255, 255)",
        align="center"
    ).set_start(start_time).set_duration(duration))
    x = GetXCenter(txt_clip, 1920)
    txt_clip = txt_clip.set_pos((x, 460))
    txt_clips += CreateSectionSubtitles(id, index, start_time+duration, cap)
    w, h = txt_clip.size
    txt_clips.append(mp.ColorClip(size=[w + 30, h + 30], color=np.array([0, 0, 0]).astype(np.uint8)).set_start(
        start_time).set_duration(duration).set_opacity(
        0.7).set_pos((x - 15, 460 - 15)))
    txt_clips.append(txt_clip)

    return txt_clips
def CreateStockClips(id, start_time, duration):
    path = os.path.join(os.path.curdir, "stock-footage")
    stock_clips = []
    for directory in os.listdir(path):
        for file in os.listdir(os.path.join(path, directory)):
            clip = mp.VideoFileClip(os.path.join(os.path.join(path, directory), file), audio=False)
            if clip.duration > 10:
                clip = clip.resize((1920, 1080)).set_duration(10)
            stock_clips.append(clip)
    clips = []
    total_duration = start_time
    prev = None
    while total_duration < duration:
        clip = random.choice(stock_clips)
        if clip == prev:
            clip = random.choice(stock_clips)
        prev = clip
        clip = clip.set_duration(random.randint(int(clip.duration/2), int(clip.duration)))
        clips.append(clip.set_start(total_duration))
        total_duration += clip.duration
    clips[len(clips)-1] = clips[len(clips)-1].set_duration(clips[len(clips)-1].duration-(total_duration-duration))
    return clips
def GetXCenter(clip, background):
    w1, h1 = clip.size
    x = (background - w1) / 2
    return x