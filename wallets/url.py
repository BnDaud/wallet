from rest_framework.routers import DefaultRouter
from django.urls import path , include
from .views import WalletViewSet

app_name="wallets"
routes = DefaultRouter()

routes.register("wallets", WalletViewSet , basename="wallets")




urlpatterns = [path("", include(routes.urls))]

