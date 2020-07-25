import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import io
import os
import sys
from PIL import Image

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 2

p = pyaudio.PyAudio()  # Create an interface to PortAudio

def extract_samples(sample_file, dest_file): 
    wf = wave.open(sample_file, 'rb')
    stream_out = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    recordings = []

    finished = False
    while not finished: 
        frames = []
        for i in range(0, int(fs / chunk * seconds)):
            data = wf.readframes(chunk)
            if len(data) == 0: 
                finished = True
            frames.append(data)

        frames = list(frames)
        fullFrames = []
        for frame in frames: 
            ns = np.fromstring(frame, np.int16)
            for s in ns: 
                fullFrames.append(s)

        print("\rRead " + str(len(recordings)) + " " + str(seconds) + "s recordings", end='')

        if not finished: 
            recordings.append(fullFrames)

    stream_out.close()

    offset = 0
    for rec in recordings: 
        plt.clf()
        plt.axis("off")
        plt.ylim(bottom=-33000, top=33000)
        plt.plot(rec, color="black")

        buf = io.BytesIO()
        plt.savefig(buf, bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        w, h = img.size
        img = img.crop((30, 8, w - 30, h - 8))
        img.save(dest_file + "-" + str(offset) + ".png")
        offset += 1

files = os.listdir("negatives-raw")
num = 0
for sample in files: 
    num += 1
    dest = "negatives/sample-" + str(num)
    try: 
        extract_samples("negatives-raw/" + sample, dest)
    except: 
        print("Caught error when processing: " + sample)
    print("\rWrote " + dest, end="")



p.terminate()

