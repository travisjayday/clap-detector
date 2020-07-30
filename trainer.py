import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import cv2

np.random.seed(0)

negatives_dir = "data/negatives/"
positives_dir = "data/positives/"
checkpoints_path = "checkpoints/cp.ckpt"
checkpoints_dir = os.path.dirname(checkpoints_path)

training_ratio = 0.72    # use 70% of dataset for training
validating_ratio = 0.14  # use 15% for validation
                        # use 15% for testing

#455, 373

img_width = 455 // 2
img_height = 373 // 2

positives = []
negatives = []

s_img = None

def read_samples(from_dir, int_arr, label):
    print("HELEO")
    for sample in os.listdir(from_dir):
        if not sample.endswith("png"): continue
        print("\rReading: " + from_dir + sample, end="")
        img = cv2.imread(from_dir + sample, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, dsize=(img_width, img_height), interpolation=cv2.INTER_CUBIC)
        img = img[:, :, 0]

        img = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        s_img = img

        img = np.expand_dims(img, -1)
        int_arr.append(np.array([img, label]))

print("Reading data...")
read_samples(positives_dir, positives, 1)
print('')
read_samples(negatives_dir, negatives, 0)
print('')

print(s_img)

print("Read {} positive samples with dimens {}".format(len(positives), positives[0][0].shape))
print("Read {} negative samples with dimens {}".format(len(negatives), negatives[0][0].shape))

dataset = np.array(positives + negatives)
np.random.shuffle(dataset)

print("Created dataset of size {}".format(len(dataset)))

num_train = int(np.floor(len(dataset) * training_ratio))
num_val = int(np.ceil(len(dataset) * validating_ratio))
num_test = len(dataset) - num_train - num_val

train_samples = dataset[0: num_train]
val_samples = dataset[num_train: num_train + num_val]
test_samples = dataset[num_train + num_val : ]

unpack_samples = lambda samples : (np.array([i for i, l in samples]), np.array([l for i, l in samples]))

train_images, train_labels = unpack_samples(train_samples)
val_images, val_labels = unpack_samples(val_samples)
test_images, test_labels = unpack_samples(test_samples)

print("Got {} training samples, {} validation samples, {} testing samples".format(
    len(train_samples), len(val_samples), len(test_samples)))

print("Importing TF...")

import tensorflow as tf
from tensorflow.keras import datasets, layers, models
from model import create_model

print("Creating model...")
model = create_model(img_width, img_height)

print(model.summary())

if len(sys.argv) == 1: 
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoints_path,
                                                     save_weights_only=True,
                                                     period=11,
                                                     verbose=1) 
    history = model.fit(train_images, train_labels, epochs=11, 
                        validation_data=(val_images, val_labels), callbacks=[cp_callback])#, class_weight={0: 0.5})

    test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)
else: 
    model.load_weights("checkpoints/cp.ckpt")
    test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)

print("Test Accuracy: " + str(test_acc))

