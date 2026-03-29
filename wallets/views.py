from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
# Create your views here.
from .walletserial import WalletSerial
from .models import Wallet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .services import send_asset , ERC20_ABI , execute_swap
from web3 import Web3
import os
from transactions.models import Transaction

SUPPORTED_TOKENS = {
    # --- Matches your Frontend list exactly ---
    #"ETH":  "0x0000000000000000000000000000000000000000",
    "USDC": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
    "UNI":  "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "WETH": "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14",
    "WBTC": "0x29f39dE984eBb3f4d05373303d94ED0516244301", # Corrected for Sepolia
    "USDT": "0x7169D38820dfd117C3FA1f22a697dBA58d90bA06",
    "LINK": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
    "DAI":  "0xFF34B3d4Aee8ddCd6F9AFFFB6Fe49bD371b8a357",
    "POL":  "0x455e53CBB86018Ac2B8092FdCd39d8444aFFC3F6", # Corrected for Sepolia
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    
    # --- Extra ones you mentioned earlier ---
    "CORE": "0x4b4A29502516BC859048384A0D81211F29dd5d99",
    "PEPE": "0x2db4A205367B809276945037E90dE26E4028D5A0",
    "ARB":  "0x98431DDc27633f7315Aa2c153233529bb241445a",
    "OP":   "0x4200000000000000000000000000000000000042",
    "AAVE": "0x88541670E5CDc35107e914B045b84ad495EE7097"
}


class WalletViewSet(ReadOnlyModelViewSet):

    serializer_class = WalletSerial
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user = self.request.user)
    

    @method_decorator(never_cache)
    @action(detail=False, methods=["get"])
    def me(self, request):
        wallet = self.get_queryset().first()
        if not wallet:
            return Response({"Error": "Wallet Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
        
        # 1. Fetch Native ETH Balance
        eth_balance_wei = w3.eth.get_balance(wallet.address, 'pending')
        balances = {
            "ETH": float(w3.from_wei(eth_balance_wei, 'ether'))
        }
    
        # 2. Fetch ERC-20 Token Balances
        for symbol, token_address in SUPPORTED_TOKENS.items():
            # Prevent the loop from overwriting the Native ETH balance!
            if symbol == "ETH":
                continue 
                
            try:
                contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
                decimals = contract.functions.decimals().call()
                raw_balance = contract.functions.balanceOf(wallet.address).call()
                balances[symbol] = float(raw_balance / (10 ** decimals))
            except Exception:
                balances[symbol] = 0.0
    
        serializer = self.get_serializer(wallet)
        data = serializer.data
        data['balances'] = balances # Append the live balances to the response
    
        return Response(data)



    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Path: /api/wallets/withdraw/"""
        wallet = self.get_queryset().first()
        if not wallet:
             return Response({"Error": "Wallet Not Found"}, status=status.HTTP_404_NOT_FOUND)
             
        to_address = request.data.get('to_address')
        amount = request.data.get('amount')
        
        # NEW: Accept an optional token_address from the frontend request
        token_address = request.data.get('token_address') 

        if not to_address or not amount:
            return Response({"error": "Missing to_address or amount"}, status=status.HTTP_400_BAD_REQUEST)

        # Call the new universal send_asset function
        tx_hash = send_asset(wallet, to_address, float(amount), token_address)
        
        if tx_hash:

            
            asset_withdrawn = token_address if token_address else "ETH"

            Transaction.objects.create(
                wallet=wallet,
                tx_hash=tx_hash,
                transaction_type='WITHDRAWAL',
                from_token=asset_withdrawn, # What they sent
                to_token=to_address,        # Where they sent it
                amount=amount
            )
            return Response({
                "message": "Transaction sent!",
                "tx_hash": tx_hash,
                "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash}"
            })
        return Response({"error": "Transaction failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)\
        

    @action(detail=False, methods=['post'])
    def swap(self, request):
        """Path: /api/wallets/swap/"""
        wallet = self.get_queryset().first()
        if not wallet:
             return Response({"Error": "Wallet Not Found"}, status=status.HTTP_404_NOT_FOUND)
             
        from_token = request.data.get('from_token')
        to_token = request.data.get('to_token')
        amount = request.data.get('amount')

        if not from_token or not to_token or not amount:
            return Response({"error": "Missing from_token, to_token, or amount"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tx_hash = execute_swap(wallet, from_token, to_token, float(amount))

            Transaction.objects.create(
                wallet=wallet,
                tx_hash=tx_hash,
                transaction_type='SWAP',
                from_token=from_token,
                to_token=to_token,
                amount=amount
            )
            return Response({
                "message": "Swap successful!",
                "tx_hash": tx_hash,
                "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash}"
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)