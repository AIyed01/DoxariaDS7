# train.py
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf

if tf.config.list_physical_devices('GPU'):
    print("GPU is available!")
else:
    print("GPU is not available!")

def build_model(input_shape=(224, 224, 3), num_classes=3):
    base_model = MobileNetV2(include_top=False, weights="imagenet", input_shape=input_shape)
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=base_model.input, outputs=outputs)
    return model

def train_model(model, train_gen, val_gen, epochs=10):
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    es = EarlyStopping(patience=3, restore_best_weights=True)
    model.fit(train_gen, validation_data=val_gen, epochs=epochs, callbacks=[es])
    model.save("model.h5")  # Save after training
    return model
