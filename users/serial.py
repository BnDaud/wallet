from .models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class UserSerial(ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # SECURITY: Prevent users from verifying themselves via the API
    is_kyc_verified = serializers.BooleanField(read_only=True)
    kyc_verified_key = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'is_kyc_verified', 
            'kyc_verified_key', 
            'is_created', 
            'is_updated', 
            'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):
        # Use a default of None so it doesn't crash if they don't update their password
        password = validated_data.pop("password", None)

        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)