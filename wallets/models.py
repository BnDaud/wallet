from django.db import models
from django.conf import settings


# Create your models here.


class Wallet(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL , on_delete=models.CASCADE)

    address = models.CharField(max_length=100 , unique=True)

    thirdweb_wallet_id =  models.CharField(max_length=100 , unique=True)

    created_at = models.DateTimeField(auto_now_add= True)


    def __str__(self):
        return "{} - {}".format(self.user.email , self.address)
