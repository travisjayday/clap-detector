import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np 
import io
import os
import sys
from PIL import Image
import matplotlib.cm as cm
from scipy import signal
from scipy.io import wavfile
import matplotlib.colors as colors
import matplotlib.cbook as cbook

debug = False

# Takes a 2 second raw clapping .wav and converts it to numpy frames
def wav2sample(sample_file, dest_file): 
    try: 
        sample_rate, samples = wavfile.read(sample_file)
    except: 
        print("Failed to read: " + sample_file)
        return 

    frequencies, times, X = signal.spectrogram(samples, sample_rate, scaling="spectrum")

    plt.clf()
    plt.imshow(X, cmap="gray", norm=colors.LogNorm(vmin=X.min(), vmax=X.max()),)

    plt.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    w, h = img.size
    img = img.crop((10, 9, w - 9, h - 10))
    buf.close()

    print("Hellow Wrote " + dest_file)
    if debug:
        img.show()
    else: 
        img.save(dest_file)

# Takes a 2 second raw clapping .wav and converts it to numpy frames
def extract_positive_sample(p, sample_file): 

    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second
    seconds = 2

    try:
        wf = wave.open(sample_file, 'rb')
    except: 
        print("FAILEDD TO READ " + str(sample_file))
        return
    stream_out = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

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

    stream_out.close()

    return fullFrames

def convert_sample(recording, dest_file, debug=True): 
    plt.clf()
    plt.axis("off")
    plt.ylim(bottom=-33000, top=33000)
    plt.plot(recording, color="black")

    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    w, h = img.size
    img = img.crop((30, 8, w - 30, h - 8))

    if debug:
        plt.show()
    else: 
        img.save(dest_file)


if __name__ == "__main__": 
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    files = os.listdir("positives-raw")
    num = 0
#    files = files[0:5]
    for sample in files: 
        num += 1
        dest = "positives/sample-" + str(num) + ".png"
        recording = wav2sample("positives-raw/" + sample, dest)
        #convert_sample(recording, dest)
        print("\rWrote " + dest, end="")

    p.terminate()

