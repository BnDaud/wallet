from .models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class UserSerial(ModelSerializer):
    password = serializers.CharField(write_only = True)
    class Meta:
        model = User
        fields = ['id', 'email', 'is_staff', "is_created", "is_updated" , "password"]

    

    def create(self, validated_data):

        pword = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(pword)

        user.save()
        return user

    def update(self, instance, validated_data):

        password = validated_data.pop("password")


        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)

