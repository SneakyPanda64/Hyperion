import random
from collections import Counter
import ftp
import util
import json
import os
import shutil
import tqdm
import logging
from youtube_api import YouTubeDataAPI
import requests
import re
def GetRandomTopic(genre):
    keywords = (util.complete(
        prompt=f"Write a list of unique and interesting keywords relating to {genre}:\n\n-",
        max_tokens=128,
        temperature=1,
        model="text-davinci-002"
    ).choices[0].text).strip().split("-")
    keywords = [i.strip() for i in keywords]
    keyword = random.choice(keywords)

    topics = (util.complete(
        #prompt=f"Write a list of 5 interesting beginner topics relating to {genre} and {keyword}:",
        prompt=f"Write a list of 5 interesting beginner topics on where {keyword} is used in the context of {genre}:\n\n-",
        max_tokens=256,
        model="text-davinci-002"
    ).choices[0].text).replace("\n", "").split("-")
    topic = (util.complete(
        prompt=f"Write a short, unique and interesting title relating to {random.choice(topics)} title without involving numbers:",
        max_tokens=20,
        temperature=1,
        model="text-davinci-002"
    )).choices[0].text.strip().replace("\"", "").replace("\'", "")
    encoded = util.base64UrlEncode(topic)
    if (encoded in os.listdir(os.path.join(os.path.curdir, "scripts"))) or (encoded in ftp.listScripts()):
        GetRandomTopic(genre)
    logging.debug(f"Keyword {keyword}, Topics {topics}, Topic {topic}")
    return topic
def GetSubTopics(topic, genre):
    text = util.complete(
        prompt=f"Write a list of around 7 beginner topics relating to what is {topic} in the context of {genre}:\n\n*",
        temperature=0
    )
    logging.debug(f"topic: {topic}, sub topics {text.choices[0].text}")
    subtopics = text.choices[0].text.strip().split("*")
    subtopics = [i.strip() for i in subtopics if i]
    return subtopics
    # for i, v in enumerate(text.choices[0].text.strip().replace("\n\n", "\n").split("\n")):
    #     texts.append(v.split(f"{i+1}. ")[1])
    # return texts
def GetPassage(passages, topic, subtopics, genre):
    text = f"Expand greatly upon the topic of {topic.replace(':', '')} in the context of {genre} summarised for a 9th grader:\n"
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
        model="text-curie-001",
        max_tokens=128,
        stop=[f"\n{len(passages)+2}.", f"\n\n{len(passages)+2}.", f"\n\n\n{len(passages)+2}."],
        presence_penalty=1
    )
    response = response_complete.choices[0].text.strip()
    logging.debug(f"passage length {len(response)}")
    if len(response) > 750 or len(response) < 10:
        return False
    words = 0
    sentence = ""
    for v in response.split("\n"):
        if words <= 70:
            words += len(v.split(" "))
            sentence += v + " "
    response = sentence.strip()
    response_edit = util.edit(
        response,
        "Replace all non-characters with their spoken counterpart. And fix grammar. And also change all numbered lists to comma seperated lists"
    )
    return response_edit.replace("[", "").replace("]", "").strip()
def GetScriptTags(topic):
    yt = YouTubeDataAPI(os.getenv("YOUTUBE_DATA_API_KEY"))
    max_results = 25
    result = (yt.search(topic, max_results=max_results))
    tags = []
    hashtags = []
    for v in tqdm.tqdm(result):
        id = (str(v).split("\'")[3])
        r = requests.get(f"https://www.googleapis.com/youtube/v3/videos?key={os.getenv('YOUTUBE_DATA_API_KEY')}&fields=items(snippet(description,tags))&part=snippet&id={id}")
        try:
            hashtags += re.findall(r'\B#\w*[a-zA-Z]+\w*', (r.json()["items"][0]["snippet"]["description"]))
            tags += (r.json()["items"][0]["snippet"]["tags"])
        except:
            pass
    # YouTube TAGS
    tags = [x.lower().replace("\\", "").strip() for x in tags]
    logging.debug(f"Tags {tags}")
    c = Counter(tags)
    chars = 0
    top_tags = []
    for i, v in enumerate(c.most_common()):
        chars += len(v[0])
        if chars < 200:
            top_tags.append(v[0])
    logging.debug(f"Top Tags {top_tags}")
    # YouTube Hashtags
    hashtags = [x.lower().strip() for x in hashtags]
    logging.debug(f"Hashtags {hashtags}")
    hashtags = [x.strip() for x in hashtags if not re.search('short', x)]
    c = Counter(hashtags)
    top_hashtags = [x[0] for x in c.most_common()][:5]
    if len(hashtags) < 8:
        logging.debug("Not enough hashtags found, using top 5 tags as replacement.")
        top_hashtags = ["#" + v.join("") for v in top_tags[:5]]
    logging.debug(f"Top Hashtags {top_hashtags}")

    return top_tags, top_hashtags
    # with open(path, "w") as f:
    #     j["tags"] = top_tags
    #     j["hashtags"] = top_hashtags
    #     json.dump(j, f)
def GetVideoScript(genre,):
    logging.info("Getting video script.")
    topic = GetRandomTopic(genre)
    logging.info(f"topic {topic}")
    subtopics = GetSubTopics(topic=topic, genre=genre)
    logging.info(f"subtopics {subtopics}")
    if len(subtopics) > 10:
        return False
    logging.debug("getting summary for topic")
    summary = (util.complete(
        prompt=f"Write a summary for the following topic in the form of a youtube description in the context of {genre}:\n\ntopic: {topic}\n\nsummary:",
        temperature=0,
        model="text-curie-001"
    )).choices[0].text.strip().replace("\"", "")
    logging.info(f"summary {summary}")
    passages = []
    for i in range(len(subtopics)):
        passage = GetPassage(passages, topic, subtopics, genre)
        if passage != False:
            passages.append(passage)
        else:
            return False
    tags, hashtags = GetScriptTags(f"{subtopics[0]} in {genre}")
    script_dict = {
        "topic": topic,
        "summary": summary,
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