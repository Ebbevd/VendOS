from django.db import models

# Create your models here.
class PaymentModel(models.Model):
    product_slot = models.CharField(max_length=10, null=True)
    stripe_session_id = models.CharField(max_length=255)
    most_recent_intent = models.CharField(max_length=255, blank=True, null=True, default=None)
    amount = models.IntegerField(null=True)  # euros
    paid = models.BooleanField(default=False)
    test = models.BooleanField(default=True)  # True if created in test mode

    def __str__(self):
        return f"Payment for product slot {self.product_slot} - Paid: {self.paid}"
    
class RefundModel(models.Model):
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.IntegerField()  # amount in cents
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refunded = models.BooleanField(default=False)
    test= models.BooleanField(default=True)  # True if created in test mode

    def __str__(self):
        return f"Refund {self.stripe_refund_id} for charge {self.stripe_charge_id} - Amount: {self.amount}"