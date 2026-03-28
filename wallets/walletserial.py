from .models import Wallet
from rest_framework.serializers import ModelSerializer , SerializerMethodField

from .services import get_live_balance


class WalletSerial(ModelSerializer):

    balance = SerializerMethodField()


    class Meta:
        model = Wallet
        fields = ['id', 'user', 'address', 'balance'] # 'user' must be here!


    def get_balance(self , obj):

        return get_live_balance(obj.address)