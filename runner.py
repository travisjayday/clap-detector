import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import cv2
import pyaudio
from PIL import Image
import io 

import tensorflow as tf
from tensorflow.keras import datasets, layers, models
from model import create_model

np.random.seed(0)

img_width = 455 // 3
img_height = 373 // 3

print("Creating model...")
model = create_model(img_width, img_height)

print(model.summary())

model.load_weights("checkpoints/cp.ckpt")


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

cv2.namedWindow("chunk1", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("chunk2", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("chunk3", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("main", cv2.WINDOW_AUTOSIZE)
one_second_iter = int(fs / chunk * 2)
frames = []

def plot_chunk(fr):
    plt.clf()
    plt.axis("off")
    plt.ylim(bottom=-33000, top=33000)
    plt.plot(fr, color="black")

    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    w, h = img.size
    img = img.crop((30, 8, w - 30, h - 8))
    img = np.array(img)

    img = cv2.resize(img, dsize=(img_width, img_height), interpolation=cv2.INTER_CUBIC)

    img = img[:, :, 0]
    img = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

    img = np.expand_dims(img, -1)

    img = img[None, ...]
    return img

lastSecondFrames = []
i = 0
while True: 
    data = in_stream.read(chunk, exception_on_overflow=False)
    frames.append(data)

    # 2 seconds passed
    if i == one_second_iter: 
        i = 0
        frames = list(frames)
        fullFrames = []
        for frame in frames: 
            ns = np.fromstring(frame, np.int16)
            for s in ns: 
                fullFrames.append(s)
        chunk1 = plot_chunk(lastSecondFrames + fullFrames[0: len(fullFrames) // 2])
        main = plot_chunk(fullFrames)
#        cv2.imshow("chunk1", chunk1)
#        cv2.imshow("main", main)
#        cv2.waitKey(1)
        frames = []
        p1 = model(main)[0][0].numpy()
        p2 = model(chunk1)[0][0].numpy()
        print(str(p1) + " " + str(p2))
        if p1 > 0.92 or p2 > 0.92: 
            print("CAPPPPP")
        lastSecondFrames = [x for x in fullFrames[len(fullFrames) // 2 : ]]
    i+= 1

sys.quit()
test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)

print("Test Accuracy: " + str(test_acc))

