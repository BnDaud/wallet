from django.contrib import admin
from .models import Transaction
# Register your models here.


class TransactionsAdmin(admin.ModelAdmin):
    list_display=["wallet" ,"amount", "from_token","to_token","timestamp","tx_hash"]


admin.site.register(Transaction , TransactionsAdmin)