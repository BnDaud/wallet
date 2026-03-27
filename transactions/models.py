from django.db import models

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('WITHDRAWAL', 'Withdrawal'),
        ('SWAP', 'Swap'),
        ('DEPOSIT', 'Deposit'),
    )

    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, related_name='transactions')
    tx_hash = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    from_token = models.CharField(max_length=100, null=True, blank=True)
    to_token = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=36, decimal_places=18)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type} | {self.amount} | {self.tx_hash[:10]}..."