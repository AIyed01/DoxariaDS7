# preprocess.py
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def create_generators(X_train, y_train, X_val, y_val):
    train_aug = ImageDataGenerator(rotation_range=15, width_shift_range=0.1,
                                   height_shift_range=0.1, zoom_range=0.1)
    val_aug = ImageDataGenerator()

    train_gen = train_aug.flow(X_train, y_train, batch_size=32)
    val_gen = val_aug.flow(X_val, y_val, batch_size=32)
    return train_gen, val_gen
