import ftp
import youtube
import multiprocessing
import logging
import sys
import os
import time

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=[
        logging.FileHandler(filename=os.path.join("logs", f"{int(time.time())}.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])
    #youtube.uploadVideo("V2h5IEFsZ29yaXRobXMgTWF0dGVyIGluIE1hY2hpbmUgTGVhcm5pbmc")
    ftp = multiprocessing.Process(target=ftp.initialise_connection)
    yt = multiprocessing.Process(target=youtube.autoChecker)
    ftp.start()
    yt.start()
    ftp.join()
    yt.join()
