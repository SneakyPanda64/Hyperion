import logging

import mutagen
import torch
import torchaudio
from time import time, sleep
import os
import tqdm
import whisper
from base64 import urlsafe_b64encode, urlsafe_b64decode
import shutil
from google.cloud import speech
import json
import openai
import librosa
from pydub import AudioSegment
from torch.backends.mkl import verbose
from tortoise.api import TextToSpeech, MODELS_DIR
from tortoise.utils.audio import load_audio, load_voices
from tortoise.utils.text import split_and_recombine_text

openai.api_key = "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"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "hyperion.json"

logging.info("loading transcription model")
model = whisper.load_model("base.en")
def transcribe(path):
    logging.debug(f"transcribing audio file in path {path}")
    result = model.transcribe(os.path.join(path))
    time = librosa.get_duration(filename=path)
    dict = None
    for v in result['segments']:
        start = 0
        logging.debug(f"start, {v['start']}, end, {v['end']}, text, {v['text']}")
        if dict is None:
            dict = {
                "text": [{
                    "text": v["text"].strip(),
                    "start": v["start"] + start,
                    "end": v["end"] + start
                }],
                "start": v["start"] + start,
                "end": v["end"] + start
            }
        else:

            new_dict = dict
            end_time = v["end"] + new_dict["text"][0]["start"]
            if end_time > time:
                end_time = time
            new_dict["text"].append({
                "text": v["text"].strip(),
                "start": v["start"] + new_dict["text"][0]["start"],
                "end": end_time
            })
            new_dict["end"] = v["end"]
            dict = new_dict

    return dict

def tts(text, voice, preset, path):
    tts = TextToSpeech(models_dir=MODELS_DIR, enable_redaction=False)
    seed = int(time())
    voice_sel = [voice]
    voice_samples, conditioning_latents = load_voices(voice_sel, ["voices"])
    all_parts = []
    length = 0 # len(str(text).split("."))
    for v in text:
        split = v.split(".")
        split = [x for x in split if x]
        if len(split) < 1:
            length += 1
        else:
            length += len(split)
    logging.info(f"processing {length} tts sections")
    if length > 45:
        return False
    with tqdm.tqdm(total=length) as pbar:
        for i, text in enumerate(text):
            logging.debug(f"Text-to-speech: {text}")
            all_sub_parts = []
            texts = text.split(".")
            texts[:] = [x for x in texts if x]
            for j, v in enumerate(texts):
                v = v.strip()
                if v[len(v)-1] != "?":
                    v += "."
                logging.debug(f"[#{j+1}] Subsection: {v}")
                gen = tts.tts_with_preset(v, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                                          preset=preset, k=1, use_deterministic_seed=seed, verbose=False, cvvp_amount=0.5)
                gen = gen.squeeze(0).cpu()
                all_sub_parts.append(gen)
                pbar.update(1)
            all_parts += all_sub_parts
            full_sub_audio = torch.cat(all_sub_parts, dim=-1)
            torchaudio.save(os.path.join(path, f'audio-{i}.wav'), full_sub_audio, 24000)
        full_audio = torch.cat(all_parts, dim=-1)
        torchaudio.save(os.path.join(path, "audio.wav"), full_audio, 24000)
    return True
    # logging.debug(f"audio finished total elapsed time: {int(time())-total_time} seconds.")
def complete(prompt, model='text-davinci-002', temperature=0.7, max_tokens=256, top_p=1, frequency_penalty=0,
         presence_penalty=0, stop="", n=1, echo=False):
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
    return response
def edit(text, instruction, temperature=0.7):
    try:
        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=text,
            instruction=instruction,
            temperature=temperature,
            top_p=1
        )
        if len(response.choices[0].text) > len(text) * 1.2:
            return text
    except:
        logging.debug("[Edit/Openai] Rate limited retrying in 7s")
        sleep(7)
        return edit(text, instruction, temperature)

    return response.choices[0].text
def base64UrlEncode(data):
    return urlsafe_b64encode(data.encode("utf-8")).rstrip(b'=').decode("utf-8")


def base64UrlDecode(base64Url):
    base64Url = base64Url.encode("utf-8")
    padding = b'=' * (4 - (len(base64Url) % 4))

    return urlsafe_b64decode(base64Url + padding).decode("utf-8")
def mkdir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

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