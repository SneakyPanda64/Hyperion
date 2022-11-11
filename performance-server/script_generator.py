import ftp
import util
import json
import os
import shutil

def GetRandomTopic(genre):
    with open("genre.json", "r") as f:
        contents = (json.loads(f.read()))
    texts = []
    i = 0
    while True:
        if i > 3:
            return False
        text = ""
        for j, v in enumerate(contents[genre] + texts):
            text = text + f"{j + 1}. {v}\n"
        response = util.complete(
            prompt=f"Write a list of {i+3} interesting topics relating to {genre}:\n\n{text.strip()}",
            temperature=1,
            top_p=1,
            max_tokens=25,
            model="text-davinci-002",
        )
        text = response.choices[0].text
        print(i, text.strip().replace(f"{i+3}. ", ""))
        search = text.split(f"{i+3}. ")[1]
        texts.append(search)
        encoded = util.base64UrlEncode(search)
        if (encoded not in os.listdir("scripts")) and (encoded not in ftp.listScripts()):
            return search
        i = i + 1
def GetSubTopics(topic, quantity, genre):
    text = util.complete(
        prompt=f"Write a list of {quantity} topics relating to {genre} and \"{topic}\":\n\n",
        temperature=0
    )
    texts = []
    for i, v in enumerate(text.choices[0].text.strip().replace("\n\n", "\n").split("\n")):
        texts.append(v.split(f"{i+1}. ")[1])
    return texts
def GetPassage(passages, topic, subtopics, genre):
    text = f"Expand greatly upon the topic of \"{topic}\" in the context of {genre} in british english:\n"
    for i, v in enumerate(subtopics):
        prefix = text + "\n" + f"{i + 1}. {v}\n\n"
        if i < len(passages):
            text = prefix + f"{passages[i]}\n"
        else:
            text = prefix
            break
    print("Getting passage..")
    response_complete = util.complete(
        prompt=f"{text}",
        temperature=1,
        model="text-curie-001",
        max_tokens=500,
        stop=[f"{len(passages)+2}. "],
    )
    response_edit = util.edit(response_complete.choices[0].text.strip(), "Replace all non-characters with their spoken counterpart.")
    return response_edit.choices[0].text.replace("-", "").replace("[", "").replace("]", "").strip()
def GetPassageTags(passages, genre):
    passages_textwrap = util.textwrap(" ".join(passages), 2000)
    responses = []
    for v in passages_textwrap:
        response = util.complete(
            prompt=f"Extract tags that are directly related to \"{genre}\" from the following passage of text in a comma seperated list format:\n\npassage: {v.strip()}\n\ntags:",
            model="text-babbage-001",
            temperature=0
        )
        text = response.choices[0].text
        print(text)
        responses += (text.split(", "))
    results = []
    for v in [i.strip() for i in responses]:
        if v not in results:
            results.append(v)
    return results
def GetVideoScript(genre, subtopics):
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
    tags = GetPassageTags(passages, genre)
    dict = {
        "topic": topic,
        "genre": genre,
        "subTopics": subtopics,
        "passages": passages,
        "tags": tags
    }
    encoded = util.base64UrlEncode(topic)
    path = os.path.join(os.path.curdir, "scripts", encoded)
    os.mkdir(path)
    with open(os.path.join(path, 'script.json'), "w") as fp:
        json.dump(dict, fp)
    return encoded