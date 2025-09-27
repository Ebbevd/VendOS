from django.apps import AppConfig
from django.conf import settings


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
    def ready(self):
            from .setup_webhook import update_stripe_webhook
            # Replace with your actual webhook ID
            if settings.DEBUG:
                update_stripe_webhook(settings.STRIPE_WH_ID_TEST)
            else:
                update_stripe_webhook(settings.STRIPE_WH_ID_LIVE)