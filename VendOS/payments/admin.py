from django.contrib import admin
from .models import PaymentModel, RefundModel

# Register your models here.
admin.site.register(PaymentModel)
admin.site.register(RefundModel)