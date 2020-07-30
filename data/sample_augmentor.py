from pydub import AudioSegment
import pyaudio
from pydub.playback import play 
import io
from extract_negative_samples import extract_negative_samples
from extract_positive_samples import extract_positive_sample, convert_sample
import wave
import numpy as np
import os

mixPositivesWithNegatives = False
mixNegativesWithNegatives = True

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 2

positives_dir = "positives-raw/"
negatives_dir = "negatives-raw/"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

raw_neg_samples = []
raw_neg_sample_files = os.listdir(negatives_dir)
#raw_neg_sample_files = raw_neg_sample_files[0:1]
for fname in raw_neg_sample_files: 
    print("Examining {}{}".format(negatives_dir, fname))
    raw_neg_samples += extract_negative_samples(p, negatives_dir + fname)
    print("\nLoaded a total of {} of two second raw negative samples".format(len(raw_neg_samples)))
raw_neg_samples = np.array(raw_neg_samples)
np.random.shuffle(raw_neg_samples)

if mixPositivesWithNegatives: 
    raw_pos_samples = []
    raw_pos_samples_files = os.listdir(positives_dir)
    #raw_pos_samples_files = raw_pos_samples_files[0:12]
    for fname in raw_pos_samples_files:
        print("Examining {}{}   \r".format(positives_dir, fname), end="")
        raw_pos_samples.append(extract_positive_sample(p, positives_dir + fname))
    print("Loaded a total of {} of two second raw positive samples".format(len(raw_pos_samples)))
    raw_pos_samples = np.array(raw_pos_samples)
    np.random.shuffle(raw_pos_samples)


print("Shuffled loaded samples...")

def save_to_buf(buf, recording):
    wf = wave.open(buf, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(recording))
    wf.close()
    buf.seek(0)

for i in range(len(raw_neg_samples)):
    if mixPositivesWithNegatives:
        j = np.random.randint(0, len(raw_pos_samples))
        raw_pos = raw_pos_samples[j]
    else:
        j = np.random.randint(0, len(raw_neg_samples))
        raw_pos = raw_neg_samples[j]

    raw_neg = raw_neg_samples[i]

    pos_buf = io.BytesIO()
    neg_buf = io.BytesIO()

    save_to_buf(pos_buf, raw_pos)
    save_to_buf(neg_buf, raw_neg)

    track1 = AudioSegment.from_file(pos_buf)
    track2 = AudioSegment.from_file(neg_buf)

    combined = track1.overlay(track2)

    if mixPositivesWithNegatives:     
        fname = "positives/gen-" + str(i) + ".png"
    else:
        fname = "negatives/gen-" + str(i) + ".png"

    print ("Generated recording " + fname + "\r", end="")
    res_buf = io.BytesIO()
    combined.export(res_buf, format='wav')
    res_buf.seek(0)

    #song = AudioSegment.from_wav(res_buf)
    #play(song)
    #res_buf.seek(0)
    
    recording = extract_positive_sample(p, res_buf)
    convert_sample(recording, fname, debug=False)

p.terminate()
