from django.urls import path
from . import views
from .views import admin_login,recognize_face,predict_image,user_login
from .views import translate_data,handle_translation_and_speech,UserCreateView,UserListView,UserDeleteView
from .views import save_scanned_document
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
   path("api/user_login/",user_login,name="user_login"),
   path("api/recognize-face/", recognize_face, name="recognize_face"),
   path('api/translate/', translate_data, name='translate_data'),
   path('api/text-to-speech/', handle_translation_and_speech, name='handle_translation_and_speech'),
   path('api/admin-login/', admin_login, name='admin_login'),
   path('api/users/', UserCreateView.as_view(), name='user-create'),
   path('api/users/list/', UserListView.as_view(), name='user-list'),
   path('api/users/delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
   path('api/classify/', predict_image, name='predict_image'),
   path('api/save-scanned-document/', save_scanned_document, name='save_scanned_document'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)