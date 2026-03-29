import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from wallets.models import Wallet
from .models import Transaction
from rest_framework import viewsets, permissions
from .models import Transaction
from .transactionsserial import TransactionSerializer

from decimal import Decimal


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)



@method_decorator(csrf_exempt, name='dispatch')
class AlchemyWebhookView(APIView):
    """
    Endpoint for Alchemy Notify. 
    Path: /api/transactions/webhook/alchemy/
    """
    # No JWT authentication required here because Alchemy is the one calling it
    authentication_classes = [] 
    permission_classes = []

    def post(self, request):
        # 1. Print the raw data to Render Logs so we can see what Alchemy sent
        print(f"DEBUG: Received Webhook Data: {request.data}")

        try:
            # Alchemy usually nests data under 'event'
            event = request.data.get('event', {})
            activity = event.get('activity', [])

            if not activity:
                print("DEBUG: No activity found in this webhook payload.")
                return Response({"status": "no activity"}, status=status.HTTP_200_OK)

            for item in activity:
                to_address = item.get('toAddress')
                from_address = item.get('fromAddress')
                raw_value = item.get('value')
                asset = item.get('asset') 
                tx_hash = item.get('hash')

                # Case-insensitive search for the wallet
                wallet = Wallet.objects.filter(address__iexact=to_address).first()
                
                if not wallet:
                    print(f"DEBUG: Received transfer for {to_address}, but it's not in our DB.")
                    continue 

                if Transaction.objects.filter(tx_hash=tx_hash).exists():
                    print(f"DEBUG: Transaction {tx_hash} already exists. Skipping.")
                    continue

                # Create the transaction
                new_tx = Transaction.objects.create(
                    wallet=wallet,
                    tx_hash=f"Deposit - {tx_hash}",
                    transaction_type='DEPOSIT',
                    from_token=from_address,
                    to_token=asset,
                    amount=Decimal(str(raw_value)) if raw_value else 0
                )
                print(f"SUCCESS: Created Deposit Transaction for {wallet.user.email}")

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR in Webhook: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
