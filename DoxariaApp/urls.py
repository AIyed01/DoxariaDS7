from django.urls import path
from . import views
from .views import admin_login,recognize_face,predict_image
from .views import translate_data,handle_translation_and_speech,UserCreateView,UserListView,UserDeleteView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
   path("api/recognize-face/", recognize_face, name="recognize_face"),
   path('api/translate/', translate_data, name='translate_data'),
   path('api/text-to-speech/', handle_translation_and_speech, name='handle_translation_and_speech'),
   path('api/admin-login/', admin_login, name='admin_login'),
   path('api/users/', UserCreateView.as_view(), name='user-create'),
   path('api/users/list/', UserListView.as_view(), name='user-list'),
   path('api/users/delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
   path('api/classify/', predict_image, name='predict_image'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)