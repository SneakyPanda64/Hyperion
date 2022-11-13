import random
from collections import Counter
import ftp
import util
import json
import os
import shutil
import logging
from youtube_api import YouTubeDataAPI
import requests
import re
def GetRandomTopic(genre):
    keyword = (util.complete(
        prompt=f"Write a single unique and interesting keyword relating to basic {genre}:",
        max_tokens=25,
        model="text-curie-001"
    ).choices[0].text).strip()
    keyword = "algorithms"
    topics = (util.complete(
        #prompt=f"Write a list of 5 interesting beginner topics relating to {genre} and {keyword}:",
        prompt=f"Write a list of 5 interesting beginner topics on where {keyword} is used in the context of \"{genre}\":\n-",
        max_tokens=256,
        model="text-curie-001"
    ).choices[0].text).replace("\n", "").split("-")
    topic = (util.complete(
        prompt=f"Write a short, unique and interesting title relating to the theory of \"{topics[random.randint(0, len(topics)-1)]}\" in the form of a video essay title:",
        max_tokens=20,
        temperature=1,
        model="text-davinci-002"
    )).choices[0].text.strip().replace("\"", "")
    encoded = util.base64UrlEncode(topic)
    if (encoded in os.listdir("scripts")) or (encoded in ftp.listScripts()):
        GetRandomTopic(genre)
    logging.debug(f"Keyword {keyword}, Topics {topics}, Topic {topic}")
    return topic
def GetSubTopics(topic, quantity, genre):
    text = util.complete(
        prompt=f"Write a list of {quantity} beginner topics relating to what is \"{topic}\" in the context of {genre}:\n\n",
        temperature=0
    )
    texts = []
    for i, v in enumerate(text.choices[0].text.strip().replace("\n\n", "\n").split("\n")):
        texts.append(v.split(f"{i+1}. ")[1])
    return texts
def GetPassage(passages, topic, subtopics, genre):
    text = f"Expand greatly upon the topic of \"{topic}\" in the context of {genre} summarised for a 9th grader:\n"
    for i, v in enumerate(subtopics):
        prefix = text + "\n" + f"{i + 1}. {v}\n\n"
        if i < len(passages):
            text = prefix + f"{passages[i]}\n"
        else:
            text = prefix
            break
    response_complete = util.complete(
        prompt=f"{text}",
        temperature=1,
        model="text-davinci-002",
        max_tokens=128,
        stop=[f"{len(passages)+2}.", f"{len(passages)+1}."],
    )
    response_edit = util.edit(
        response_complete.choices[0].text.strip(),
        "Replace all non-characters with their spoken counterpart. And fix grammar."
    )
    return response_edit.choices[0].text.replace("-", "").replace("[", "").replace("]", "").strip()
def GetScriptTags(topic):
    yt = YouTubeDataAPI(os.getenv("YOUTUBE_DATA_API_KEY"))
    result = (yt.search(topic, max_results=25))
    tags = []
    hashtags = []
    for v in result:
        id = (str(v).split("\'")[3])
        r = requests.get(f"https://www.googleapis.com/youtube/v3/videos?key={os.getenv('YOUTUBE_DATA_API_KEY')}&fields=items(snippet(description,tags))&part=snippet&id={id}")
        try:
            hashtags += re.findall(r'\B#\w*[a-zA-Z]+\w*', (r.json()["items"][0]["snippet"]["description"]))
            tags += (r.json()["items"][0]["snippet"]["tags"])
        except:
            pass
    # Youtube Hashtags
    tags = [x.lower().replace("\\", "").strip() for x in tags]
    hashtags = [x.lower().strip() for x in hashtags]
    logging.debug(f"Hashtags {hashtags}")
    hashtags = [x.strip() for x in hashtags]
    c = Counter(hashtags)
    top_hashtags = [x[0] for x in c.most_common()][:5]
    logging.debug(f"Top Hashtags {top_hashtags}")
    # Youtube TAGS
    logging.debug(f"Tags {tags}")
    c = Counter(tags)
    chars = 0
    top_tags = []
    for i, v in enumerate(c.most_common()):
        chars += len(v[0])
        if chars < 200:
            top_tags.append(v[0])
    logging.debug(f"Top Tags {top_tags}")
    return top_tags, top_hashtags
    # with open(path, "w") as f:
    #     j["tags"] = top_tags
    #     j["hashtags"] = top_hashtags
    #     json.dump(j, f)
def GetVideoScript(genre, subtopics):
    logging.info("Getting video script.")
    topic = GetRandomTopic(genre)
    subtopics = GetSubTopics(
        topic=topic,
        quantity=subtopics,
        genre=genre
    )
    passages = []
    for i in range(len(subtopics)):
        passage = GetPassage(passages, topic, subtopics, genre)
        passages.append(passage)
    tags, hashtags = GetScriptTags(topic)
    script_dict = {
        "topic": topic,
        "genre": genre,
        "subTopics": subtopics,
        "passages": passages,
        "tags": tags,
        "hashtags": hashtags
    }
    encoded = util.base64UrlEncode(topic)
    path = os.path.join(os.path.curdir, "scripts", encoded)
    os.mkdir(path)
    with open(os.path.join(path, 'script.json'), "w") as fp:
        json.dump(script_dict, fp)
    return encoded