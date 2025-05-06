from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    image = models.ImageField(upload_to='users/',default='users/default.png')  # Save images in media/users/

    metadata = models.JSONField(default=dict)
    class Meta:
        db_table = 'users'
    @classmethod
    def create_user(cls, email, password, **extra_fields):
        user = cls(
            email=email,
            password=make_password(password),
            **extra_fields
        )
        user.save()
        return user

from django.utils import timezone
class ScannedDocument(models.Model):
    user = models.CharField(max_length=100)
    document_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(default=timezone.now)
    detected_fields = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("rejected", "Rejected")
    ], default="pending")

    class Meta:
        db_table = 'scanned_documents'