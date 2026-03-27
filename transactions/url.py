from django.urls import path, include
from .views import AlchemyWebhookView , TransactionViewSet
from rest_framework.routers import DefaultRouter


app_name = "transactions"

router = DefaultRouter()

router.register("history" , TransactionViewSet , basename="history")


urlpatterns = [

    path("" , include(router.urls)),
    path('webhook/alchemy/', AlchemyWebhookView.as_view(), name='alchemy-webhook'),
]