#!/usr/bin/env python
# coding: utf-8

# In[3]:


from PIL import Image
import pytesseract
import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# In[55]:


import pytesseract
from PIL import Image

def ocr_with_stopwords(image_path, stopwords):
    image = Image.open(image_path)
   
    text = pytesseract.image_to_string(image)
   
    words = text.split()
   
    for word in words:
        if word.lower() in stopwords:
            print(f"Found stopword: {word}")
            return word  
   
    print("No stopwords found.")
    return None

stopwords = ["assurance", "star"]

image_path = "C:/Users/user/Downloads/test3.jpg"

ocr_with_stopwords(image_path, stopwords)


# In[53]:


# Télécharger les stop words
nltk.download('stopwords')
french_stop_words = stopwords.words('french')

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='fra+ara', config="--psm 6")
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def extract_text_from_folder(folder_path):
    texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            text = extract_text_from_image(image_path)
            texts.append(text)
    return texts

# Extract text from both folders
bulletin_texts = extract_text_from_folder("C:/Users/user/Downloads/doxaria/bulletin/")
other_texts = extract_text_from_folder("C:/Users/user/Downloads/doxaria/ordonnance/")

# Create a DataFrame
data = {
    "text": bulletin_texts + other_texts,
    "label": [1] * len(bulletin_texts) + [0] * len(other_texts)
}
df = pd.DataFrame(data)

# Shuffle the dataset
df = df.sample(frac=1).reset_index(drop=True)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, random_state=42)

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(max_features=1000, stop_words=french_stop_words)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train a Logistic Regression model with hyperparameter tuning
model = LogisticRegression(class_weight='balanced')
param_grid = {'C': [0.01, 0.1, 1, 10, 100]}
grid_search = GridSearchCV(model, param_grid, cv=5)
grid_search.fit(X_train_tfidf, y_train)

# Evaluate the model
y_pred = grid_search.predict(X_test_tfidf)

# Save the model and vectorizer
with open("document_classifier.pkl", "wb") as model_file:
    pickle.dump(grid_search, model_file)
with open("tfidf_vectorizer.pkl", "wb") as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

def classify_document(image_path, confidence_threshold=0.55):
    """
    Classify a new document as 'bulletin de soin', 'ordonnance', or 'unrecognized type'.
    """
    with open("document_classifier.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    with open("tfidf_vectorizer.pkl", "rb") as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    
    text = extract_text_from_image(image_path)
    text_tfidf = vectorizer.transform([text])
    probabilities = model.predict_proba(text_tfidf)[0]
    max_probability = max(probabilities)
    
    if max_probability < confidence_threshold:
        return "unrecognized type"
    
    prediction = model.predict(text_tfidf)
    return "bulletin de soin" if prediction[0] == 1 else "ordonnance"


# In[52]:


new_document_path = "C:/Users/user/Downloads/test3.jpg"
result = classify_document(new_document_path)
print(f"The document is classified as: {result}")

