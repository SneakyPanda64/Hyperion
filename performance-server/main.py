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
import torch

def main(repeat=1, preset="standard"):
    repeated = 0
    while repeated < repeat:
        if not os.path.exists("stock-footage"):
            os.mkdir("stock-footage")
            for v in ["coding", "technology", "computers"]:
                os.mkdir(os.path.join("stock-footage", v))
                stock.GetFootage(os.path.join("stock-footage", v), v, 10)
        id = script.GetVideoScript(
            "theory of computer science"
        )
        if not id:
            logging.critical(f"Failed to generate video script")
        elif not audio.CreateAudio(id=id, speed=preset):
            logging.critical(f"Failed to generate audio")
        elif not thumbnail.GenerateThumbnail(id):
            logging.critical(f"Failed to generate thumbnail")
        elif not video.CreateVideo(id):
            logging.critical(f"Failed to create video")
        elif not ftp.uploadScript(id):
            logging.critical(f"Failed to upload video to ftp server")
        else:
            logging.info(f"Video finished id: {id}")
            repeated += 1
    logging.info(f"Finished video creation ({repeated}/{repeat})")

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=os.getenv("LOGGING_LEVEL"), force=True, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(filename=os.path.join("logs", f"{int(time.time())}.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])
    if not torch.cuda.is_available():
        logging.critical("GPU not detected")
    else:
        logging.critical(f"GPU detected")
    if not ftp.login():
        logging.critical("FTP server could not be reached")
    else:
        #ftp.uploadScript("VGhlIFNlY3JldCBMaWZlIG9mIHBpeGVscw")
        main(repeat=int(os.getenv("MAIN_REPEATS")), preset=os.getenv("TTS_PRESET"))
