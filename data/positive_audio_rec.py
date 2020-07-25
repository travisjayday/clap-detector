import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import io
import os

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 2

p = pyaudio.PyAudio()  # Create an interface to PortAudio
in_stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)

def get_sample(): 
    os.chdir("positives")
    sample_num = 0
    for fil in os.listdir(): 
        if fil.startswith("sample-"): 
            num = int(fil.split("-")[1].split(".")[0])
            if num > sample_num:
                sample_num = num
    sample_num += 1
    os.chdir("..")
    print("sample num is: " + str(sample_num))

    filename = "positives-raw/sample-" + str(sample_num) + ".wav"


    print('Recording')

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = in_stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    # Terminate the PortAudio interface

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    stream_out = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    for f in frames:
        stream_out.write(f)

    frames = list(frames)
    fullFrames = []
    for frame in frames: 
        ns = np.fromstring(frame, np.int16)
        for s in ns: 
            fullFrames.append(s)

    stream_out.close()

    ft = np.fft.fft(fullFrames[100:])
    mag = np.abs(ft) ** 2
    plt.clf()
    plt.axis("off")
    plt.ylim(bottom=-33000, top=33000)
    plt.plot(fullFrames, color="black")

    plt.savefig("positives/sample-" + str(sample_num) + ".png", bbox_inches='tight')

for _ in range(10):
    get_sample()

# Stop and close the stream 
in_stream.stop_stream()
in_stream.close()

p.terminate()

