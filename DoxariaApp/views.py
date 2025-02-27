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
import pygame
from gtts import gTTS

# Charger les visages connus depuis le dossier People/face/
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

def text_to_speech(phrase, language):
    # Map des langues
    lang_map = {
        "english": "en",
        "french": "fr",
        "arabic": "ar"
    }

    if language.lower() not in lang_map:
        print("Language not supported.")
        return

    # Générer le fichier audio dans un buffer en mémoire
    tts = gTTS(text=phrase, lang=lang_map[language.lower()], slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)  # Remettre le pointeur au début du fichier audio

    # Initialiser pygame et lire le fichier
    pygame.mixer.init()
    pygame.mixer.music.load(fp, "mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


@csrf_exempt
def handle_translation_and_speech(request):
    if request.method == "POST":
        try:
            # Récupérer les données envoyées
            data = json.loads(request.body)
            phrase = data.get("phrase")  # Phrase à traduire
            language = data.get("language", "english")  # Langue cible (par défaut anglais)

            if not phrase:
                return JsonResponse({"error": "Phrase is required"}, status=400)

            # Traduire les données
            translated_data = translate_data(data, language)

            # Utiliser la phrase traduite pour la synthèse vocale
            translated_phrase = translated_data.get("phrase", phrase)

            # Appeler la fonction text_to_speech pour la lecture du texte traduit
            text_to_speech(translated_phrase, language)

            return JsonResponse({"translated": translated_data})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
