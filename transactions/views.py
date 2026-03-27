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
        try:
            # Alchemy sends data inside an 'event' object
            data = request.data.get('event', {})
            network = data.get('network')
            activity = data.get('activity', [])

            for item in activity:
                to_address = item.get('toAddress')
                from_address = item.get('fromAddress')
                amount = item.get('value')
                asset = item.get('asset') # e.g., 'ETH', 'USDC'
                tx_hash = item.get('hash')

                # 1. Check if the receiving address belongs to a wallet in your database
                try:
                    # Make sure to compare addresses in lowercase
                    wallet = Wallet.objects.get(address__iexact=to_address)
                except Wallet.DoesNotExist:
                    continue # Not our user, skip

                # 2. Prevent duplicate entries (Alchemy sometimes retries webhooks)
                if Transaction.objects.filter(tx_hash=tx_hash).exists():
                    continue

                # 3. Save the deposit!
                Transaction.objects.create(
                    wallet=wallet,
                    tx_hash=tx_hash,
                    transaction_type='DEPOSIT',
                    from_token=from_address, # Where it came from
                    to_token=asset,          # What they deposited (ETH, USDC)
                    amount=amount
                )

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)