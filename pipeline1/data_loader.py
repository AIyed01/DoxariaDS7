import os
import cv2
import numpy as np

IMG_SIZE = 224
CLASSES = ["Bulletin_de_soin", "Ordonnance", "Other"]

def load_images_from_folder(folder, classes=CLASSES):
    X, y = [], []
    for label, category in enumerate(classes):
        folder_path = os.path.join(folder, category)
        if not os.path.exists(folder_path):
            print(f"Missing folder: {folder_path}")
            continue
        for img_name in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path)
            if img is None:
                print(f"Unreadable image: {img_path}")
                continue
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            img = img / 255.0
            X.append(img)
            y.append(label)
    return np.array(X), np.array(y)

def load_data(train_folder, test_folder):
    # Load training data
    X_train, y_train = load_images_from_folder(train_folder)
    
    # Load testing data
    X_test, y_test = load_images_from_folder(test_folder)

    return X_train, y_train, X_test, y_test
