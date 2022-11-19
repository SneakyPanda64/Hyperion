import util
import os
import json

def CreateAudio(id, speed):
    path = os.path.join(os.path.curdir, "scripts", id)
    with open(os.path.join(path, "script.json"), "r") as f:
        contents = json.loads(f.read())
    tts_texts = []
    for i, v in enumerate(contents["subTopics"]):
        tts_texts.append(v)
        tts_texts.append(contents["passages"][i])
    print(tts_texts)
    util.mkdir(os.path.join(path, "audio"))
    if not util.tts(tts_texts, "rslash", speed, os.path.join(path, "audio")):
        return False
    return True