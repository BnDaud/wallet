from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    explorer_url = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 
            'transaction_type', 
            'from_token', 
            'to_token', 
            'amount', 
            'tx_hash', 
            'explorer_url', 
            'timestamp'
        ]

    def get_explorer_url(self, obj):
        return f"https://sepolia.etherscan.io/tx/{obj.tx_hash}"