from django.urls import path
from . import views
from .views import admin_login,recognize_face
from .views import translate_data,handle_translation_and_speech
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
   path("api/recognize-face/", recognize_face, name="recognize_face"),
   path('api/translate/', translate_data, name='translate_data'),
   path('api/text-to-speech/', handle_translation_and_speech, name='handle_translation_and_speech'),
   path('api/admin-login/', admin_login, name='admin_login'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)