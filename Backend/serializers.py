from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'user_type', 'password']
        # For hashing password
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animals
        fields = ('AnimalId', 'CommonName', 'ScientificName')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('ImageId', 'Img', 'Caption', 'Contributer')
