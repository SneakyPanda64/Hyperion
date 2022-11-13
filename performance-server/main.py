import script_generator as script
import audio_generator as audio
import video_generator as video
import thumbnail_generator as thumbnail
import stock as stock
import shutil
import os
import util
import ftp
import logging
import time
import sys
from dotenv import load_dotenv

def logs():
    print("[Logs] Resetting logs")
    util.mkdir(os.path.join(os.path.curdir, "logs", "gpt3"))

def main():
    id = script.GetVideoScript(
        genre="computer science",
        subtopics=1 # around 30s per subtopic
    )
    if not id:
        print("[Script] Conflict error")
        return
    audio.CreateAudio(
        id=id,
        speed="ultra_fast"
    )
    thumbnail.GenerateThumbnail(id)
    video.CreateVideo(id)
    if not ftp.uploadScript(id):
        print("[FTP] Upload failed due to: conflict")
        return

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(filename=os.path.join("logs", f"{int(time.time())}.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])
    if not ftp.login():
        logging.critical("FTP server could not be reached") # https://www.googleapis.com/youtube/v3/videos?key={API-key}&fields=items(snippet(title,description,tags))&part=snippet&id={video_id}
    else:
        print(script.GetVideoScript("computer science", 2))
