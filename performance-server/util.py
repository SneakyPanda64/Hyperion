import torch
import torchaudio
from time import time, sleep
import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
import shutil
from google.cloud import speech
import json
import openai
from pydub import AudioSegment
from tortoise.api import TextToSpeech, MODELS_DIR
from tortoise.utils.audio import load_audio, load_voices
from tortoise.utils.text import split_and_recombine_text

openai.api_key = "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"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "hyperion.json"

def transcribe(path):
    print("[TTS] Transcribing audio file")
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        audio_channel_count = 1,
        language_code="en-US",
        enable_word_time_offsets=True,
    )
    with open(path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    results = (client.recognize(config=config, audio=audio))
    return results

def tts(text, voice, preset, path, mono=False):
    total_time = int(time())
    print("[TTS] Loading model")
    tts = TextToSpeech(models_dir=MODELS_DIR)
    model_time = int(time())-total_time
    print(f"[TTS] Model loading time: {model_time} seconds")
    seed = int(time())
    voice_sel = [voice]
    voice_samples, conditioning_latents = load_voices(voice_sel)
    all_parts = []
    for i, text in enumerate(text):
        print(f"[TTS] Text: {text}")
        all_sub_parts = []
        texts = text.split(".")
        texts[:] = [x for x in texts if x]
        for j, v in enumerate(texts):
            v = v.strip()
            if v[len(v)-1] != "?":
                v += "."
            print(f"#{j+1} Subtext -> {v}")
            gen = tts.tts_with_preset(v, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                                      preset=preset, k=1, use_deterministic_seed=seed)
            gen = gen.squeeze(0).cpu()
            all_sub_parts.append(gen)
        all_parts += all_sub_parts
        full_sub_audio = torch.cat(all_sub_parts, dim=-1)
        torchaudio.save(os.path.join(path, f'audio-{i}.wav'), full_sub_audio, 24000)
        if mono:
            sound = (AudioSegment.from_wav(os.path.join(path, f'audio-{i}.wav'))).set_channels(1).set_frame_rate(16000)
            sound.export(os.path.join(path, f"mono-{i}.wav"), format='s16le', bitrate='16k')
    full_audio = torch.cat(all_parts, dim=-1)
    torchaudio.save(os.path.join(path, "audio.wav"), full_audio, 24000)
    if mono:
        sound = (AudioSegment.from_wav(os.path.join(path, "audio.wav"))).set_channels(1).set_frame_rate(16000)
        sound.export(os.path.join(path, "mono.wav"), format='s16le', bitrate='16k')
    print(f"[TTS] Finished, total elapsed time: {int(time())-(total_time-model_time)} seconds.")
    print(f"[TTS] Model loading took: {model_time} seconds")

def complete(prompt, model='text-davinci-002', temperature=0.7, max_tokens=256, top_p=1, frequency_penalty=0,
         presence_penalty=0, n=1, stop="", echo=False):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        n=n,
        stop=stop,
        echo=echo
    )
    with open(os.path.join(os.path.curdir, "logs", "gpt3", f"{response.created}.txt"), "w") as f:
        f.write(prompt + "\n" + "=" * 26 + "\n" + json.dumps(response))
    return response
def edit(text, instruction, temperature=0):
    try:
        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=text,
            instruction=instruction,
            temperature=temperature,
            top_p=1
        )
    except:
        print("[Edit/Openai] Rate limited retrying in 10s")
        sleep(10)
        return edit(text, instruction, temperature)
    return response
def base64UrlEncode(data):
    return urlsafe_b64encode(data.encode("utf-8")).rstrip(b'=').decode("utf-8")


def base64UrlDecode(base64Url):
    base64Url = base64Url.encode("utf-8")
    padding = b'=' * (4 - (len(base64Url) % 4))

    return urlsafe_b64decode(base64Url + padding).decode("utf-8")
def mkdir(path):
    try:
        shutil.rmtree(path)
    except:
        pass
    os.mkdir(path)
# def textwrap(text, max):
#     sentences = []
#     words = []
#     chars = 0
#     for v in text.split(" "):
#         chars = chars + len(v)
#         words.append(v)
#         if chars >= max:
#             sentences.append(" ".join(words))
#             words = []
#             chars = 0
#             print(len(v))
#     sentences.append(" ".join(words))
#     sentences[:] = [x for x in sentences if x]
#     return sentences
def textwrap(text, max):
    sentences = []
    words = []
    chars = 0
    for v in text.split(" "):
        words.append(v)
        chars = chars + len(v)
        if chars >= max:
            sentences.append(" ".join(words))
            words = []
            chars = 0
    sentences.append(" ".join(words))
    sentences[:] = [x for x in sentences if x]
    return sentences
def GetCenter(bw, bh, iw, ih):
    x = (bw - iw) / 2
    y = (bh - ih) / 2
    return (x,y)