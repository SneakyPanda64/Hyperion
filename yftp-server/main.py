import ftp
import youtube
import multiprocessing
import logging
import sys
import os
import time
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()

    logging.basicConfig(level=logging.DEBUG, force=True, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(filename=os.path.join("logs", f"{int(time.time())}.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])
    if not os.path.exists("scripts"):
        os.mkdir("scripts")
    if not os.path.exists("logs"):
        os.mkdir("logs")
    ftp = multiprocessing.Process(target=ftp.initialise_connection)
    yt = multiprocessing.Process(target=youtube.autoChecker)
    ftp.start()
    yt.start()
    ftp.join()
    yt.join()
