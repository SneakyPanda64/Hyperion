import script_generator as script
import audio_generator as audio
import video_generator as video
import thumbnail_generator as thumbnail
import stock as stock
import shutil
import os
import util
import ftp


def logs():
    print("[Logs] Resetting logs")
    util.mkdir(os.path.join(os.path.curdir, "logs", "gpt3"))

def main():
    id = script.GetVideoScript(
        genre="computer science",
        subtopics=10 # around 30s per subtopic
    )
    if not id:
        print("[Script] Conflict error")
        return
    audio.CreateAudio(
        id=id,
        speed="standard"
    )
    video.CreateVideo(id)
    if not ftp.uploadScript(id):
        print("[FTP] Upload failed due to: conflict")
        return

if __name__ == '__main__':
    logs()
    #script.GetVideoScript("computer science", subtopics=2)
    #print(util.transcribe(os.path.join("scripts", "V2hhdCBhcmUgdGhlIGJlbmVmaXRzIG9mIHVzaW5nIGJsb2NrY2hhaW4gdGVjaG5vbG9neSBpbiB0aGUgY29tcHV0ZXIgc2NpZW5jZSB3b3JsZD8", "audio", "mono.wav")))
    #text = "For example, C plus plus is a popular object oriented. Programming language" # There are many different types of programming languages. Some popular types of programming languages. "  #" Java is a popular language for developing web applications. Python is a popular programming language for developing scientific applications. Ruby is a popular language for developing web applications and small to medium size software projects."
    #util.tts([text], "rslash", "ultra_fast", "test")
    #ftp.listScripts()
    #ftp.uploadScript("SG93IGNhbiBJIGltcHJvdmUgbXkgcHJvZ3JhbW1pbmcgc2tpbGxzPw")
    while True:
        try:
            main()
        except:
            print("Error occured")
    #util.tts(["I'm going to speak this"], "rslash", "standard", "test")
    #video.CreateVideo("SG93IGRvIGNvbXB1dGVyIHZpcnVzZXMgc3ByZWFkPw")
    #stock.SearchVideos("V2hhdCBpcyB0aGUgZGlmZmVyZW5jZSBiZXR3ZWVuIGEgcHJvZ3JhbW1pbmcgbGFuZ3VhZ2UgYW5kIGEgbWFya3VwIGxhbmd1YWdlPw", "coding", 5)
    #video.CreateSectionSubtitles("V2hhdCBhcmUgdGhlIGJlbmVmaXRzIG9mIHVzaW5nIGJsb2NrY2hhaW4gdGVjaG5vbG9neSBpbiB0aGUgY29tcHV0ZXIgc2NpZW5jZSB3b3JsZD8", 1, 0)
    #audio.CreateAudio("V2hhdCBhcmUgdGhlIGJlbmVmaXRzIG9mIHVzaW5nIGJsb2NrY2hhaW4gdGVjaG5vbG9neSBpbiB0aGUgY29tcHV0ZXIgc2NpZW5jZSB3b3JsZD8")
    #print(script.GetRandomTopic("computer science"))
    # passages = [
    #     "Computer viruses typically spread when files that are infected with a virus are clicked on or opened by a user. The virus then downloads and executes on the targeted computer. Virus writers typically distribute their viruses through email, bulletin board systems (BBSs), or through links in online articles or message boards. Once a computer is infected with a virus, it can be difficult to remove.",
    #     "A computer virus can infect a file by penetrating the computer's security mechanisms and editing the file's contents. Once infected, the virus can automatically launch when the file is opened, or it can infect a file by exploiting a vulnerability in the software that is used to open the file."
    # ]
    # print(script.GetPassageTags(passages, "computer science"))
    #script.GetVideoScript("computer science", 2)
    #subtopics = (GetSubTopics("What is the difference between a virus and a worm?"))
    # passages = []
    # for i in range(2):
    #     passage = (GetPassage(passages, "What is the difference between a virus and a worm?",
    #                ['What is the difference between a virus and a worm?', 'How do computer viruses work?', 'What are the most common types of computer viruses?'], "computer science"))
    #     passages.append(passage)
    # print(passages)
    # util.tts(
    #     text=["hello this is an example title", "this is a test body"],
    #     voice="random",
    #     preset="ultra_fast",
    #     path="audio"
    # )

