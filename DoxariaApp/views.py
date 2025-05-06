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
import hashlib
import uuid
import pygame
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import tensorflow as tf
from io import BytesIO
from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from django.utils import timezone
from .models import ScannedDocument

"""
## super user login
ADMIN_CREDENTIALS = {
    "admin@doxaria.tn": "password123"
}
"""
"""
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

"""
"""sumary_line

"""


# Get the path of the current working directory where manage.py is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Correct the model path to point to the same directory as manage.py
MODEL_PATH = os.path.join(BASE_DIR, "modeleclassification.h5")
# Try to load the model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    MODEL_LOADED = True
except Exception as e:
    print(f"Failed to load model: {e}")
    MODEL_LOADED = False

# Check if the model is loaded
if MODEL_LOADED:
    print("Model loaded successfully!")
else:
    print("Failed to load model.")


# Labels des classes
class_labels = ["Bulletin de soin", "Ordonnance", "Other"]

@csrf_exempt
def predict_image(request):
    if not MODEL_LOADED:
        return JsonResponse({'error': 'Model not loaded'}, status=503)
    
    if request.method == 'POST':
        img_file = request.FILES.get('image')
        if img_file:
            try:
                img_bytes = BytesIO(img_file.read())  # Convertir en BytesIO
                img = tf.keras.preprocessing.image.load_img(img_bytes, target_size=(224, 224))
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array /= 255.0

                predictions = model.predict(img_array)
                predicted_class = np.argmax(predictions, axis=1)[0]
                confidence = float(np.max(predictions)) * 100
                predicted_label = class_labels[predicted_class]

                return JsonResponse({
                    'label': predicted_label,
                    'confidence': f"{confidence:.2f}%"
                })
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Aucune image reçue'}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)








# Admin face image path
try:
    ADMIN_IMAGE_PATH = os.path.join(settings.SECURE_ROOT, 'admin_face.jpg')
    if not os.path.exists(ADMIN_IMAGE_PATH):
        raise ImproperlyConfigured("Admin face image not found at configured location")
except AttributeError:
    raise ImproperlyConfigured(
        "SECURE_ROOT not configured in settings. "
        "Please add SECURE_ROOT to your settings.py"
    )

@csrf_exempt
def admin_login(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"}, 
            status=405
        )

    try:
        data = json.loads(request.body)
        username = data.get("email")
        password = data.get("password")
        image_data = data.get("image")

        # Validate required fields
        if not username or not password:
            return JsonResponse(
                {"error": "username and password are required"},
                status=400
            )

        # Authenticate credentials
        user = authenticate(request, username=username, password=password)
        if not user or not user.is_superuser:
            return JsonResponse(
                {"error": "Invalid admin credentials"},
                status=401
            )

        # If no image provided, request face verification
        if not image_data:
            return JsonResponse(
                {
                    "message": "Credentials verified. Face recognition required",
                    "next_step": "face_verification"
                },
                status=202
            )

        # Verify face image - Updated to match recognize_face approach
        try:
            # Decode base64 image
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            
            # Create temp file for face comparison
            with tempfile.NamedTemporaryFile(suffix=".jpg", mode='wb', delete=False) as temp_img:
                temp_img.write(image_bytes)
                temp_path = temp_img.name
                os.chmod(temp_path, 0o644)
                
                # Load images for comparison (using the same approach as recognize_face)
                img = cv2.imread(temp_path)
                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                
                # Load admin image with same processing
                admin_img = cv2.imread(ADMIN_IMAGE_PATH)
                admin_imgS = cv2.resize(admin_img, (0, 0), None, 0.25, 0.25)
                admin_imgS = cv2.cvtColor(admin_imgS, cv2.COLOR_BGR2RGB)
                
                # Get face encodings for both images
                admin_encoding = face_recognition.face_encodings(admin_imgS)
                captured_encoding = face_recognition.face_encodings(imgS)
                
                if not admin_encoding or not captured_encoding:
                    return JsonResponse(
                        {"error": "No faces detected in one or both images"},
                        status=400
                    )
                
                # Compare faces using distance (like in recognize_face)
                faceDis = face_recognition.face_distance([admin_encoding[0]], captured_encoding[0])
                
                # Consider it a match if distance is below threshold (0.6 is default)
                if faceDis[0] > 0.6:
                    return JsonResponse(
                        {"error": "Face verification failed"},
                        status=401
                    )
                
                # Create authenticated session
                login(request, user)

                return JsonResponse({
                    "success": "Admin authenticated successfully",
                    "session_id": request.session.session_key,
                    "requires_reauth_after": 3600,  # 1 hour in seconds
                    "user" : username
                })

        except Exception as face_error:
            return JsonResponse(
                {"error": f"Face verification error: {str(face_error)}"},
                status=500
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON data"},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Server error: {str(e)}"},
            status=500
        )



import json
import base64
import cv2
import os
import tempfile
import face_recognition
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password



@csrf_exempt
def user_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        image_data = data.get("image")
        

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        # Étape 1 : Vérification de l'existence de l'utilisateur
        try:
            user = User.objects.get(email=email)
            
            filename = os.path.basename(user.image.name)
            username = os.path.splitext(filename)[0]
            
        except User.DoesNotExist:
            return JsonResponse({"error": "Email not found"}, status=401)

        # Étape 2 : Vérification du mot de passe
        if not check_password(password, user.password):
            return JsonResponse({"error": "Incorrect password"}, status=401)

        # Étape 3 : Si pas d'image, demander vérification faciale
        if not image_data:
            return JsonResponse({
                "message": "Credentials verified. Face recognition required",
                "next_step": "face_verification"
            }, status=202)

        # Verify face image - Updated to match recognize_face approach
        try:
            # Decode base64 image
            image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            
            # Create temp file for face comparison
            with tempfile.NamedTemporaryFile(suffix=".jpg", mode='wb', delete=False) as temp_img:
                temp_img.write(image_bytes)
                temp_path = temp_img.name
                os.chmod(temp_path, 0o644)
                
                # Load images for comparison (using the same approach as recognize_face)
                img = cv2.imread(temp_path)
                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                
                # Load admin image with same processing
                admin_img = cv2.imread(user.image.path)
                admin_imgS = cv2.resize(admin_img, (0, 0), None, 0.25, 0.25)
                admin_imgS = cv2.cvtColor(admin_imgS, cv2.COLOR_BGR2RGB)
                
                # Get face encodings for both images
                admin_encoding = face_recognition.face_encodings(admin_imgS)
                captured_encoding = face_recognition.face_encodings(imgS)
                
                if not admin_encoding or not captured_encoding:
                    return JsonResponse(
                        {"error": "No faces detected in one or both images"},
                        status=400
                    )
                
                # Compare faces using distance (like in recognize_face)
                faceDis = face_recognition.face_distance([admin_encoding[0]], captured_encoding[0])
                
                # Consider it a match if distance is below threshold (0.6 is default)
                if faceDis[0] > 0.6:
                    return JsonResponse(
                        {"error": "Face verification failed"},
                        status=401
                    )
                
                
                print(username)
                return JsonResponse({
                    "success": "user authenticated successfully",
                    "session_id": request.session.session_key,
                    "requires_reauth_after": 3600,  # 1 hour in seconds
                    "user" : username
                })

        except Exception as face_error:
            return JsonResponse(
                {"error": f"Face verification error: {str(face_error)}"},
                status=500
            )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)




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
            print("data " , data)
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
            print("trans data", translated_data)

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




class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        password = serializer.validated_data.get('password')
        if password:
            # Hash the password before saving the user
            hashed_password = make_password(password)
            serializer.validated_data['password'] = hashed_password
        # Save the user instance with the hashed password
        serializer.save()

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete the associated image file if it exists
        try:
            if instance.image and os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except Exception as e:
            print(f"Erreur lors de la suppression de l'image : {e}")

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



def hash_value(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

@csrf_exempt
def save_scanned_document(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received Data:", data)

            required_fields = ['user', 'document_type', 'detected_fields']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            raw_fields = data['detected_fields']
            hashed_fields = {k: hash_value(str(v)) for k, v in raw_fields.items()}

            scanned_doc = ScannedDocument.objects.create(
                user=data['user'],
                document_type=data['document_type'],
                uploaded_at=timezone.now(),
                detected_fields=hashed_fields,
                status=data.get('status', 'pending')
            )

            return JsonResponse({
                'message': 'Scanned document saved successfully',
                'document_id': str(scanned_doc.id)
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("Exception occurred:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)