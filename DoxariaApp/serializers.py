from rest_framework import serializers
from .models import User
from django.core.files.base import ContentFile
import base64

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'password', 'image', 'metadata']
        
    def create(self, validated_data):
        # Just create the user directly
        return User.objects.create(**validated_data)