from django.shortcuts import render

# Create your views here.


from .serial import UserSerial
from .models import User
from rest_framework.viewsets import ModelViewSet

class Userview(ModelViewSet):
    serializer_class = UserSerial
    queryset = User.objects.all()