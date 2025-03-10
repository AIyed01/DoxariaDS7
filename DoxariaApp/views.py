import os
import cv2
import json
import numpy as np
import face_recognition
import base64
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from deep_translator import GoogleTranslator
import io
from gtts import gTTS
from django.http import  FileResponse

import uuid
import pygame

## super user login
ADMIN_CREDENTIALS = {
    "admin@doxaria.tn": "password123"
}
# Chemin de l'image de l'admin
ADMIN_IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, "admin", "a.jpg")

@csrf_exempt
def admin_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            image_data = data.get("image")  # Peut être None au début
            print(email)
            # 🔹 Vérification des identifiants (remplace avec une vraie validation)
            if email != "admin@doxaria.tn" or password != "admin123":
                return JsonResponse({"error": "Identifiants incorrects"}, status=401)

            # 🔹 Si aucune image n'est envoyée, demander la reconnaissance faciale
            if not image_data:
                return JsonResponse({"message": "Identifiants corrects. Capturez une image."})

            # 🔹 Décoder l'image Base64 envoyée
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
                temp_img.write(image_bytes)
                temp_path = temp_img.name

            # 🔹 Charger l'image de l'admin et l'image capturée
            if not os.path.exists(ADMIN_IMAGE_PATH):
                return JsonResponse({"error": "Image de l'admin introuvable"}, status=500)

            known_image = face_recognition.load_image_file(ADMIN_IMAGE_PATH)
            captured_image = face_recognition.load_image_file(temp_path)

            # 🔹 Encoder les visages
            known_encoding = face_recognition.face_encodings(known_image)
            captured_encoding = face_recognition.face_encodings(captured_image)

            if not known_encoding or not captured_encoding:
                return JsonResponse({"error": "Aucun visage détecté"}, status=400)

            # 🔹 Comparer les visages
            match = face_recognition.compare_faces([known_encoding[0]], captured_encoding[0])
            if match[0]:
                return JsonResponse({"recognized": "ADMIN"})
            else:
                return JsonResponse({"error": "Visage non reconnu"}, status=401)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)












### reconnaissance faciale
# Charger les visages connus depuis le dossier Media/users/
path = path = os.path.join(settings.MEDIA_ROOT, 'users') 
images = []
classNames = []
encodeListKnown = []

personsList = os.listdir(path)
for cl in personsList:
    curPerson = cv2.imread(os.path.join(path, cl))
    images.append(curPerson)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodings = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(img)
        if face_encodings:
            encodings.append(face_encodings[0])
    return encodings

encodeListKnown = findEncodings(images)

@csrf_exempt
def recognize_face(request):
    if request.method == "POST":
        try:
            # Récupérer l'image envoyée
            data = json.loads(request.body)
            image_data = data.get("image")
            if not image_data:
                return JsonResponse({"error": "Aucune image reçue"}, status=400)

            # Décoder l'image Base64
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)

            # Sauvegarder temporairement l'image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
                temp_img.write(image_bytes)
                temp_path = temp_img.name

            # Charger l'image pour l'analyse
            img = cv2.imread(temp_path)
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Trouver les visages dans l'image
            faceCurentFrame = face_recognition.face_locations(imgS)
            encodeCurentFrame = face_recognition.face_encodings(imgS, faceCurentFrame)

            recognized_name = "false"

            for encodeface, faceLoc in zip(encodeCurentFrame, faceCurentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeface)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeface)
                
                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        recognized_name = classNames[matchIndex].upper()
                        break

            return JsonResponse({"recognized": recognized_name})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)



#### traduction


@csrf_exempt
def translate_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            target_language = data.get("language", "ar")  # Langue par défaut : arabe
            data.pop("language", None)  # Supprimer "language" avant traduction

            if not isinstance(data, dict):
                return JsonResponse({"error": "Format de données invalide"}, status=400)

            def translate_text(text, lang):
                if isinstance(text, str) and text.strip():
                    translated = GoogleTranslator(source="fr", target=lang).translate(text)  # ⚠️ FR forcé
                    return translated
                return text

            translated_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    translated_data[key] = translate_text(value, target_language)
                elif isinstance(value, list) and all(isinstance(item, dict) for item in value):  
                    translated_data[key] = [
                        {k: translate_text(v, target_language) for k, v in item.items()} for item in value
                    ]
                elif isinstance(value, list):  
                    translated_data[key] = [translate_text(item, target_language) for item in value]
                else:
                    translated_data[key] = value  

            return JsonResponse(translated_data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


#### text to speech

@csrf_exempt
def handle_translation_and_speech(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phrase = data.get("phrase")
            language = data.get("language", "english")
            print("data " ,phrase)
            
            translated_phrase = GoogleTranslator(source="fr", target=language).translate(phrase)

            #translated_phrase = GoogleTranslator(source="auto", target=language).translate(phrase)
            print("translated ",translated_phrase)
            # Générer le fichier audio
            tts = gTTS(text=translated_phrase, lang=language, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)

            # Jouer l'audio avec pygame
            pygame.mixer.init()
            pygame.mixer.music.load(fp, "mp3")
            pygame.mixer.music.play()

            return JsonResponse({"message": "Audio played successfully","translated_phrase":translated_phrase})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)