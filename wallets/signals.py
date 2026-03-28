from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Wallet
from .services import create_local_wallet , register_address_to_alchemy
import threading

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet_signal(sender, instance, created, **kwargs):
    if created:
        wallet_data = create_local_wallet()
     
        Wallet.objects.create(
            user=instance,
            address=wallet_data["address"],
            private_key=wallet_data["private_key"]
        )
        addr = wallet_data["address"]

        threading.Thread(target=
        register_address_to_alchemy , args=(addr,)).start()