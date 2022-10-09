from editor import generate_video
from tts import tts_process

def main():
    # tts_process("this i a test", "title.wav")
    # generate_video(1, True, False)
    generate_video(size=2, overwrite=True, tts=True)
main()

