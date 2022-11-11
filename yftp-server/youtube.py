import os
import json
from time import sleep, time
import datetime

from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

log_name = "latest.txt"
channel = Channel()
channel.login("hyperion.json", "credentials.storage")

def log(text):
    print(text)
    with open(os.path.join("logs", log_name), "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")
        f.close()
def getVideosUploaded():
    with open(os.path.join("videos.json")) as f:
        return json.loads(f.read())["uploaded"]
def uploadVideo(id):
    path = os.path.join("scripts", id)
    log(f"[Youtube] Uploading video: {id}")
    with open(os.path.join(path, "script.json")) as f:
        j = json.loads(f.read())
        description = f"{'-' * 18}\nVideo timeline\n0:00 - Introduction"
        for i, v in enumerate(j['subTopics']):
            m, s = divmod(int(j['timeline'][i]), 60)
            timestamp = f'{m:01d}:{s:02d}'
            description += f"\n{timestamp} - {v}"
        description += "\n" + ("-" * 18)
        video = LocalVideo(
            file_path=os.path.join(path, "video.mp4"),
            title=j["topic"],
            description=description,
            category="education",
            tags=j["tags"],
            default_language="en-US",
        )
        video.set_embeddable(True)
        video.set_license("youtube")
        video.set_privacy_status("public")
        video.set_public_stats_viewable(True)
        video.set_made_for_kids(True)
        video.set_thumbnail_path(os.path.join(path, "thumbnail.png"))
        video = channel.upload_video(video)
        log(f"[Youtube] Video uploaded {video.id}")
def upload():
    path = os.path.join("scripts")
    videos = getVideosUploaded()
    for id in os.listdir(path):
        log(f"[Youtube] Checking if {id} is already uploaded")
        stat = os.stat(os.path.join(path, id))
        if time()-stat.st_mtime < 30:
            log(f"[Youtube] Too risky, younger than 30s")
        else:
            if id not in videos:
                log(f"[Youtube] Uploading video: {id}")
                contents = json.loads(open(os.path.join("videos.json"), "r").read())
                with open(os.path.join("videos.json"), "w") as f:
                    videos = contents["uploaded"]
                    videos.append(id)
                    contents["uploaded"] = videos
                    json.dump(contents, f)
                uploadVideo(id)
                break
def main():
    lastUploaded = time()
    while True:
        sleep(600)
        dif = time()-lastUploaded
        date = datetime.datetime.now()
        if dif > 3600:
            log(f"Checking timezone, current hour: {date.hour}")
            if date.hour == 9 or date.hour == 15 or date.hour == 19:
                log(f"Uploading video time: {date}")
                try:
                    upload()
                except:
                    log(f"Upload failed.")
                lastUploaded = time()
        log(f"last uploaded: {int(dif)}s ago, current time: {date}")
if __name__ == '__main__':
    log_name = f"{int(time())}.txt"
    main()