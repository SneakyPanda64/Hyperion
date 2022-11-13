import ftp
import youtube
import multiprocessing


if __name__ == '__main__':
    ftp = multiprocessing.Process(target=ftp.initialise_connection)
    yt = multiprocessing.Process(target=youtube.autoChecker)
    ftp.start()
    yt.start()
    ftp.join()
    yt.join()
