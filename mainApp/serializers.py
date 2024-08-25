# myapp/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        # Validate email
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data['email']):
            raise serializers.ValidationError({"email": "Invalid email address."})
        
        # Validate username
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9-_]{3,23}$', data['username']):
            raise serializers.ValidationError({"username": "Username must be 4 to 24 characters long and start with a letter."})
        
        # Validate password
        if not re.match(r'^(?=.*[0-9])[A-Za-z\d]{8,}$', data['password']):
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long and include at least one number."})

        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
