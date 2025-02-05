"""Serializers used by the REST endpoints"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer used for signing up new Users"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ("username", "password")

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)
