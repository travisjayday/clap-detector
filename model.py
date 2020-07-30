import tensorflow as tf
from tensorflow.keras import datasets, layers, models

def create_model(img_width, img_height): 
    model = models.Sequential()

    # Images are size 455//4 x 373//4
    model.add(layers.Conv2D(32, (3, 3), activation="relu", input_shape=(img_height, img_width, 1)))
    model.add(layers.MaxPooling2D((2,2)))
    model.add(layers.Conv2D(128, (3, 3), activation="relu"))
    model.add(layers.MaxPooling2D((2,2)))
    model.add(layers.Dropout(0.25))
    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation="relu"))
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation="sigmoid"))

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(),
                  metrics=['accuracy'])

    return model


