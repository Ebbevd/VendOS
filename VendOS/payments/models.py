from django.db import models

# Create your models here.
class PaymentModel(models.Model):
    product_slot = models.CharField(max_length=10)
    stripe_session_id = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for product slot {self.product_slot} - Paid: {self.paid}"