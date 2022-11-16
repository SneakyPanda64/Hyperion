import os
import json
import shutil
from time import sleep, time
import datetime
import logging
import sys

from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo


def getVideosUploaded():
    with open(os.path.join("videos.json")) as f:
        return json.loads(f.read())["uploaded"]
def uploadVideo(id):
    path = os.path.join("scripts", id)
    channel = Channel()
    channel.login("hyperion.json", "credentials.storage")
    with open(os.path.join(path, "script.json")) as f:
        j = json.loads(f.read())
        description = f"{j['summary']}\n\n{'=-=' * 7}\nVideo timeline/Topics covered\n0:00 - Introduction"
        for i, v in enumerate(j['subTopics']):
            m, s = divmod(int(j['timeline'][i]), 60)
            timestamp = f'{m:01d}:{s:02d}'
            description += f"\n{timestamp} - {v}"
        description += f"\n{('=-=' * 7)}\n\n{' '.join(j['hashtags'])}"
        video_path = os.path.join(path, f"{'-'.join(j['tags'][0].split(' '))}.mp4")
        shutil.copyfile(os.path.join(path, "video.mp4"), video_path)
        video = LocalVideo(
            file_path=video_path,
            title=j["topic"],
            description=description,
            category=27,
            tags=j["tags"],
            default_language="en-US",
        )
        video.set_embeddable(True)
        video.set_license("creativeCommon")
        video.set_privacy_status("private")
        video.set_public_stats_viewable(True)
        video.set_made_for_kids(False)
        video.set_thumbnail_path(os.path.join(path, "thumbnail.png"))

        #video = channel.upload_video(video)
        logging.info(f"Video has been uploaded to youtube")
def upload():
    path = os.path.join("scripts")
    uploading = 0
    videos = getVideosUploaded()
    for i, id in enumerate(os.listdir(path)):
        stat = os.stat(os.path.join(path, id))
        if time()-stat.st_mtime < 30:
            logging.debug(f"#{i} [{id}] (too young > 30s)")
        else:
            if id not in videos:
                if uploading >= 1:
                    logging.debug(f"#{i} [{id}] (max uploads)")
                else:
                    logging.debug(f"#{i} [{id}] (uploading)")
                    contents = json.loads(open(os.path.join("videos.json"), "r").read())
                    videos = contents["uploaded"]
                    videos.append(id)
                    with open(os.path.join("videos.json"), "w") as f:
                        contents["uploaded"] = videos
                        json.dump(contents, f)
                    uploading += 1
                    uploadVideo(id)
            else:
                logging.debug(f"#{i} [{id}] (already uploaded)")
def autoChecker(time_period=1800):
    lastUploaded = time()
    while True:
        sleep(time_period)
        dif = time()-lastUploaded
        date = datetime.datetime.now()
        logging.debug(f"Checking if there was a video last uploaded 1h ago. Last uploaded {int(dif)}s ago")
        if dif > 3600:
            logging.debug(f"Checking if videos should be uploaded this hour.")
            # hours = [9, 15, 19]
            # if date.hour in hours:
            logging.info(f"Check passed, uploading video")
            try:
                upload()
                lastUploaded = time()
            except Exception as e:
                logging.error(f"Error occurred: {e}")
                break
