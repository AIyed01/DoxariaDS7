from django.urls import path
from . import views
from .views import recognize_face
from .views import translate_data
urlpatterns = [
   path("api/recognize-face/", recognize_face, name="recognize_face"),
   path('api/translate/', translate_data, name='translate_data'),
]
