from re import T
import subprocess
import os
import shlex
import shutil
from autocorrect import Speller
import language_tool_python
tool = language_tool_python.LanguageTool('en-GB')

def tts_process(text, fpath):
    voice = "rslash"
    preset = "ultra_fast"
    corrected_text = tool.correct(text)
    print("Text:", text, "Corrected:", corrected_text)
    text = corrected_text
    clear_files("")
    path = os.path.join(os.path.dirname(__file__) + "/tortoise-tts/tortoise/")
    f = open("input.txt", "w")
    f.write(text)
    f.close()
    try:
        command = shlex.split("python " + path + "read.py" + " --textfile input.txt --voice " + voice + " --preset " + preset + " --output_path output --candidates 1")
        subprocess.run(command)
    except:
        command = shlex.split("python " + path + "do_tts.py" + " --text \"" + text + "\" --voice " + voice + " --preset " + preset + " --output_path output/" + voice + " --candidates 1")
        subprocess.run(command)
    list_files(fpath, voice)
    
    "[TTS] Finished working on " + fpath
def tts_process_file(text):
    voice = "rslash"
    preset = "ultra_fast"
    corrected_text = tool.correct(text)
    print("Text:", text, "Corrected:", corrected_text)
    text = corrected_text
    path = os.path.join(os.path.dirname(__file__) + "/tortoise-tts/tortoise/")
    f = open("input.txt", "w")
    f.write(text)
    f.close()
    command = shlex.split("python " + path + "read.py" + " --textfile input.txt --voice " + voice + " --preset " + preset + " --output_path shorts/output --candidates 1")
    subprocess.run(command)
    shutil.move(os.path.join(os.path.dirname(__file__), "shorts/output/rslash/0.wav"), os.path.join(os.path.dirname(__file__),"shorts/test/comments.wav"))
def list_files(fpath, voice):
    directory = os.path.join(os.path.dirname(__file__), "output", voice)
    m = 0
    for filename in os.listdir(directory):
        print(directory, filename)
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            file_stats = os.stat(f)
            if (file_stats.st_size > (os.stat(m)).st_size):
                m = f
    t = os.path.join(os.path.dirname(__file__), fpath)
    print("Moving:", m, "To:", t)
    shutil.move(m, t)
def clear_files(dir):
    directory = os.path.join(os.path.dirname(__file__), "output", dir)
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            os.remove(f)
        else:
            clear_files(filename)
