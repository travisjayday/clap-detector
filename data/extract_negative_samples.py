import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import io
import os
import sys
from PIL import Image
from extract_positive_samples import wav2sample
import matplotlib.cm as cm
from scipy import signal
from scipy.io import wavfile
import matplotlib.colors as colors
import matplotlib.cbook as cbook



chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 2

# Takes a long sample wav file and cuts it up into two second piece chunks
# Returns all those recordings as frames in a list
def extract_negative_samples(p, sample_file): 

    try: 
        wf = wave.open(sample_file, 'rb')
        stream_out = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
    except: 
        print("Failed to read " + sample_file)
        return []

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

    return recordings 

def recordings2samples(recordings, dest_file):
    i = 0
    for frames in recordings: 
        wf = wave.open("/tmp/sample.wav", 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        wav2sample("/tmp/sample.wav", dest_file + "-" + str(i) + ".png")
        i += 1

def convert_samples(recordings, dest_file): 
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

if __name__ == "__main__": 
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    files = os.listdir("negatives-raw")
    num = 0
#    files = files[0: 1]
    for sample in files: 
        num += 1
        dest = "negatives/sample-" + str(num)
        try: 
            recordings = extract_negative_samples(p, "negatives-raw/" + sample)
            recordings2samples(recordings, dest)
        except Exception as e: 
            print("\nCaught error when processing: " + sample + str(e) + "\n")
        print("\rWrote " + dest, end="")

    p.terminate()

