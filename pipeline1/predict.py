# predict.py
import cv2
import numpy as np

def predict_image(model, image_path, img_size=224, class_names=None):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (img_size, img_size)) / 255.0
    pred = model.predict(np.expand_dims(img, axis=0))
    class_idx = np.argmax(pred)
    return class_names[class_idx] if class_names else class_idx
