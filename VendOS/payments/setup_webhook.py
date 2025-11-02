import stripe
from django.conf import settings
import requests
from urllib.parse import urlparse

if settings.DEBUG:
    stripe.api_key = settings.STRIPE_SK_TEST  # your test secret key
else:
    stripe.api_key = settings.STRIPE_SK_LIVE  # your live secret key

def update_stripe_webhook(webhook_id):
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("[WARINGIN] No ngrok URL found")
        pass
    parsed = urlparse(ngrok_url)
    host = parsed.netloc  # gives 'sympodial-plicately-fredia.ngrok-free.dev'

    if host not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append(host)

    try:
        # Update the webhook endpoint URL
        stripe.WebhookEndpoint.modify(
            webhook_id,
            url=f"{ngrok_url}/payments/webhook/"
        )
        print(f"Stripe webhook updated to {ngrok_url}/payments/webhook/")
    except Exception as e:
        print("Error updating webhook:", e)
        
def get_ngrok_url():
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        for t in tunnels["tunnels"]:
            if t["proto"] == "https":
                return t["public_url"]
    except Exception as e:
        print("Could not get ngrok URL:", e)
    return None