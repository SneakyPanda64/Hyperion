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


def main(repeat=1, preset="standard"):
    repeated = 0
    while True:
        if repeated >= repeat:
            break
        if not os.path.exists("stock-footage"):
            os.mkdir("stock-footage")
            for v in ["coding", "technology", "computers"]:
                os.mkdir(os.path.join("stock-footage", v))
                stock.GetFootage(os.path.join("stock-footage", v), v, 10)
        id = script.GetVideoScript(
            "computer science"
        )
        if not id:
            logging.critical(f"Failed to generate video script")
        else:
            audio.CreateAudio(
                id=id,
                speed=preset
            )
            thumbnail.GenerateThumbnail(id)
            video.CreateVideo(id)
            if not ftp.uploadScript(id):
                logging.critical(f"Failed to upload video to ftp server")
                return
            logging.info(f"Video finished id: {id}")
            repeated += 1
    logging.info(f"Finished video creation ({repeated}/{repeat})")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, force=True, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(filename=os.path.join("logs", f"{int(time.time())}.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])
    load_dotenv()

    if not ftp.login():
        logging.critical("FTP server could not be reached")
    else:
        print(script.GetRandomTopic("computer science"))
