from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import Userview

routes = DefaultRouter()

routes.register("users" , viewset= Userview, basename="users")



urlpatterns = [path("" , include(routes.urls))]

