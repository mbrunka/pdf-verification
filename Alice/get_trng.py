import sys, os
from wave import open

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "TRNG"))
from trng import trng_generate


def get_trng(sound_file_path):
    # Open the wave file and read the binary data
    w = open(sound_file_path, "rb")
    if w is None:
        print("Error: Unable to open file")
        exit()

    nframes = w.getnframes()
    # Read the audio data as a string of bytes
    audio_data = w.readframes(nframes)
    w.close()

    return trng_generate(audio_data)
