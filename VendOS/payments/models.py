from django.db import models

# Create your models here.
class PaymentModel(models.Model):
    product_slot = models.CharField(max_length=10)
    stripe_session_id = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for product slot {self.product_slot} - Paid: {self.paid}"
    
class RefundModel(models.Model):
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.IntegerField()  # amount in cents
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refunded = models.BooleanField(default=False)

    def __str__(self):
        return f"Refund {self.stripe_refund_id} for charge {self.stripe_charge_id} - Amount: {self.amount}"