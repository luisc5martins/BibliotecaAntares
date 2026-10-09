from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SlugRelatedField

from core.models import User
from uploader.models import Image
from uploader.serializers import ImageSerializer


class UserSerializer(ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8
    )

    foto_attachment_key = SlugRelatedField(
        source='foto',
        queryset=Image.objects.all(),
        slug_field='attachment_key',
        required=False,
        write_only=True,
    )

    foto = ImageSerializer(
        required=False,
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'password',
            'foto',
            'foto_attachment_key',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'groups',
        )
        depth = 1

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        user = User.objects.create(
            **validated_data
        )

        if password:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'password',
        ]

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data
        )