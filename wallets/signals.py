from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Wallet
from .services import create_thirdweb_wallet 



@receiver(post_save , sender= User)
def create_user_wallet(sender , instance , created , **kwargs):

    if created:
        wallet_data = create_thirdweb_wallet(instance.id)

        Wallet.objects.create(user = instance ,
                              address = wallet_data["address"],
                               thirdweb_wallet_id =wallet_data["id"])