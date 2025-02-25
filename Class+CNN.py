#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import cv2
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Définition des chemins des dossiers train et test
DATASET_DIR = "C:/Users/user/Downloads/dataset"
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
TEST_DIR = os.path.join(DATASET_DIR, "test")
CLASSES = ["Bulletin_de_soin", "Ordonnance", "Other"]
IMG_SIZE = 224  # Taille standard pour MobileNetV2

def load_images_from_folder(folder):
    X, y = [], []
    for label, category in enumerate(CLASSES):
        folder_path = os.path.join(folder, category)
        
        if not os.path.exists(folder_path):
            print(f"Dossier non trouvé : {folder_path}")
            continue
        
        for img_name in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path)

            if img is None:
                print(f"Impossible de lire l'image : {img_path}")
                continue
            
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            img = img / 255.0  # Normalisation
            X.append(img)
            y.append(label)

    return np.array(X), np.array(y)

# Chargement des images depuis train et test
X_train, y_train = load_images_from_folder(TRAIN_DIR)
X_test, y_test = load_images_from_folder(TEST_DIR)

# Vérification finale
if len(X_train) == 0 or len(X_test) == 0:
    raise ValueError("Les images n'ont pas été correctement chargées. Vérifie les chemins et le format des images.")


# In[2]:


# Chargement du modèle pré-entraîné
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
base_model.trainable = False  # On freeze les poids

# Ajout des couches personnalisées
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.3)(x)
output = Dense(3, activation="softmax")(x)  # 3 neurones pour 3 classes

# Création du modèle final
model = Model(inputs=base_model.input, outputs=output)

# Compilation du modèle
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# Affichage du résumé du modèle
model.summary()


# In[3]:


# Génération de données augmentées
datagen = ImageDataGenerator(rotation_range=15, zoom_range=0.2, horizontal_flip=True)

# Entraînement du modèle
history = model.fit(datagen.flow(X_train, y_train, batch_size=32),
                    validation_data=(X_test, y_test),
                    epochs=10)


# In[4]:


def predict_image(image_path, model, X_test, y_test):
    IMG_SIZE = 224  # Taille utilisée lors de l'entraînement

    # Chargement et prétraitement de l'image
    img = cv2.imread(image_path)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0  # Normalisation
    img = np.expand_dims(img, axis=0)  # Ajouter une dimension b111111atch

    # Prédiction
    predictions = model.predict(img)[0]  # Liste des probabilités pour chaque classe
    class_index = np.argmax(predictions)  # Récupérer l'index de la classe avec la plus haute probabilité
    confidence = predictions[class_index] * 100

    # Correspondance avec les classes
    class_labels = ["bulletin de soin", "ordonnance", "autre document médical"]
    class_label = class_labels[class_index]

    # 🔹 **Calcul de l'accuracy globale du modèle**
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)

    print(f"Prédiction : {class_label} | Confiance : {confidence:.2f}%")
    print(f"Accuracy globale du modèle sur test : {accuracy * 100:.2f}%")

# 🔍 Test avec une image


# In[14]:


predict_image(r"C:\Users\user\Downloads\final_processed.jpg", model, X_test, y_test)


# In[22]:


import cv2
import numpy as np
import os

template_folder = r"C:\Users\user\Downloads\dataset\train\BCNN"
test_image_path = r"C:\Users\user\Downloads\test.jpg"
output_path = r"C:\Users\user\Downloads\aligned_brightened.jpg"

def load_images_from_folder(folder):
    images = {}
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images[filename] = img
    return images

def find_best_template(test_image, templates):
    sift = cv2.SIFT_create()
    keypoints2, descriptors2 = sift.detectAndCompute(test_image, None)
    
    best_match = None
    best_match_count = 0
    best_template = None
    
    for filename, template in templates.items():
        keypoints1, descriptors1 = sift.detectAndCompute(template, None)
        if descriptors1 is None or descriptors2 is None:
            continue
        
        flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
        matches = flann.knnMatch(descriptors1, descriptors2, k=2)
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
        
        if len(good_matches) > best_match_count:
            best_match_count = len(good_matches)
            best_match = template
            best_template = filename
    
    return best_match, best_template

def align_and_brighten_image(test_image, template):
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(template, None)
    keypoints2, descriptors2 = sift.detectAndCompute(test_image, None)
    
    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
    
    if len(good_matches) >= 4:
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        h, w = template.shape
        aligned_image = cv2.warpPerspective(test_image, H, (w, h))
        
        brightened_image = cv2.convertScaleAbs(aligned_image, alpha=1.5, beta=30)
        return brightened_image
    
    return None

templates = load_images_from_folder(template_folder)
test_image = cv2.imread(test_image_path, cv2.IMREAD_GRAYSCALE)

if test_image is None or not templates:
    print("Error: Test image or templates not found!")
else:
    best_template, best_template_name = find_best_template(test_image, templates)
    
    if best_template is not None:
        print(f"Best matching template: {best_template_name}")
        result = align_and_brighten_image(test_image, best_template)
        
        if result is not None:
            cv2.imwrite(output_path, result)
            print(f"Processed image saved at: {output_path}")
        else:
            print("Failed to align images.")
    else:
        print("No good matches found. Try better-quality images.")
image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB) 
        
plt.imshow(result)
plt.axis("off") 
plt.show()


# In[24]:


import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_tables(image_path):
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert to binary using adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4
    )

    # Apply morphological operations to enhance table structures
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morphed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter small noise by setting a minimum area threshold
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 5000]

    # Get bounding boxes
    bounding_boxes = [cv2.boundingRect(cnt) for cnt in filtered_contours]
    bounding_boxes = sorted(bounding_boxes, key=lambda x: x[1])  # Sort by y-coordinate

    # Compute image area
    image_area = image.shape[0] * image.shape[1]
    
    # Compute percentage area for each table
    table_areas = [(w * h) / image_area * 100 for x, y, w, h in bounding_boxes]
    
    # Draw bounding boxes on the image
    output_image = image.copy()
    for x, y, w, h in bounding_boxes:
        cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 3)
    
    # Show detected tables
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
    plt.title("Detected Tables with Bounding Boxes")
    plt.axis("off")
    plt.show()
    
    return table_areas

# Example usage
image_path = r"C:\Users\user\Downloads\aligned_brightened.jpg"
table_percentages = detect_tables(image_path)
print("Table Area Percentages:", table_percentages)


# In[ ]:




