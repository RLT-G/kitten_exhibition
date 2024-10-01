"""Сериализаторы"""

from rest_framework import serializers
from kittens import models
from django.contrib.auth import get_user_model


User = get_user_model()


class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Breed
        fields = ['id', 'name']


class KittenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Kitten
        fields = ['id', 'name', 'breed', 'owner']


class DetailedKittenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Kitten
        fields = '__all__'
        extra_kwargs = {'owner': {'required': False}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
    
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Хэшируем пароль
        user.save()
        return user