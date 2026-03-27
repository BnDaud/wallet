from django.contrib import admin
from .models import Wallet

# Register your models here.



class WalletAdmin(admin.ModelAdmin):
    list_display = ["user", "address" ,"private_key"]



admin.site.register(Wallet , WalletAdmin)