from wave import open
from trng import trng_generate

# Open the wave file and read the binary data
w = open("TRNG/sound-samples/test.wav", "rb")
if w is None:
    print("Error: Unable to open file")
    exit()

nframes = w.getnframes()
# Read the audio data as a string of bytes
audio_data = w.readframes(nframes)
w.close()

rdat = trng_generate(audio_data)

print(rdat)
