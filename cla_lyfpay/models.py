import uuid

from django.contrib.auth.models import User
from django.db import models
from dateutil import tz


class Wallet(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self) -> str:
        return self.name

class Payment(models.Model):
    
    class Origin(models.TextChoices):  # 
        """_summary_
        - Must be formated like so : ^[0-9a-zA-Z]$
        - Must have a 
        Args:
            models (_type_): _description_
        """
        DANCING_PARTY_REGISTRATION = 'dpr', 'inscription soirée dansante'
    
    class LyfpayStatus(models.TextChoices):
        WAITING = 'WAITING', 'en attente'
        VALIDATED = 'VALIDATED', 'validé'
        REFUSED = 'REFUSED', 'refusé'
        FAILED = 'FAILED', 'échoué'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", editable=False)
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='payments')
    
    origin = models.CharField(max_length=50, choices=Origin.choices, editable=False)
    reference = models.CharField(max_length=250, editable=False)
    
    lyfpay_shop_reference = models.CharField(max_length=80, unique=True, editable=False)
    lyfpay_shop_order_reference = models.CharField(max_length=80, editable=False)
    
    lyfpay_id = models.CharField(max_length=250, null=True, blank=True, editable=False)
    lyfpay_amount = models.PositiveSmallIntegerField(editable=False)
    lyfpay_status = models.CharField(max_length=20, choices=LyfpayStatus.choices, default=LyfpayStatus.WAITING, editable=False)
    lyfpay_updated_at = models.DateTimeField(null=True, editable=False)
    
    notes = models.TextField(max_length=1000, default="", blank=True)
    
    @property
    def amount_display(self):
        return f'{int(self.lyfpay_amount // 100)}.{str(self.lyfpay_amount % 100).zfill(2)} €'

    @property
    def validated(self):
        return self.lyfpay_status == self.LyfpayStatus.VALIDATED
    
    def __str__(self) -> str:
        return self.lyfpay_shop_reference