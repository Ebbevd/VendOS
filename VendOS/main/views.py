from django.shortcuts import render, redirect
from django.contrib import messages
import subprocess
from .models import Product
from status.models import Status
import requests
import stripe
import time
from django.conf import settings

# Create your views here.
def splash_screen_view(request):
    status = Status.objects.first()
    
    if status:
        if status.errored:
            status.errored = False
            status.save()
    return render(request, "main/splash_screen.html")

# --- Helper functions --- #

def get_ngrok_url():
    """Fetch the current ngrok public HTTPS URL."""
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        for t in tunnels.get("tunnels", []):
            if t.get("proto") == "https":
                return t.get("public_url")
    except Exception as e:
        print("Could not get ngrok URL:", e)
    return None


def start_ngrok(port=8000, sleep=2):
    """Start ngrok in background if not running."""
    try:
        subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Starting ngrok tunnel on port {port}...")
        time.sleep(sleep)  # Give ngrok time to initialize
        return get_ngrok_url()
    except Exception as e:
        print("Error starting ngrok:", e)
        return None


def update_stripe_webhook(webhook_id):
    """Update the Stripe webhook endpoint to the current ngrok URL."""
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("No ngrok URL found; cannot update Stripe webhook.")
        return False

    try:
        stripe.WebhookEndpoint.modify(
            webhook_id,
            url=f"{ngrok_url}/payments/webhook/"
        )
        print(f"✅ Stripe webhook updated to {ngrok_url}/payments/webhook/")
        return True
    except Exception as e:
        print("❌ Error updating Stripe webhook:", e)
        return False


# --- Main view --- #

def order_screen_view(request):
    if settings.DEBUG:
        WEBHOOK_ID = settings.STRIPE_WH_ID_TEST
    else:
        WEBHOOK_ID = settings.STRIPE_WH_ID_LIVE

    try:
        # 1️⃣ Try to get existing ngrok URL
        ngrok_url = get_ngrok_url()
        if not ngrok_url:
            print("Ngrok not found; attempting to start it...")
            ngrok_url = start_ngrok(port=8000)
            time.sleep(2)  # wait a bit longer for ngrok to stabilize
            # 2️⃣ If we successfully got an ngrok URL, update Stripe webhook
            if ngrok_url:
                update_stripe_webhook(WEBHOOK_ID)
                context = {"time_out": 300}
                return render(request, "main/order_screen.html", context)

            else:# 3️⃣ If ngrok still failed, show error
                raise Exception("Ngrok tunnel could not be established")
        else:
            return render(request, "main/order_screen.html", context={"time_out": 300})
    except Exception as e:
        print("Error in order_screen_view:", e)
        return redirect('error_page')

    
    
def order_package(request):
    if request.method == "POST":
        slot_code = request.POST.get("slot_code")
        try:
            product = Product.objects.get(slot_id=slot_code)
            if product.stock > 0:
                # redirect to checkout
                return redirect('checkout', product_slot=slot_code)
            else:
                # Out of stock
                messages.error(request, "The selected slot is out of stock.")
                return redirect('order_screen')
        except Product.DoesNotExist:
            # Invalid slot
            messages.error(request, "The slot code you selected does not exist. Please try again.")
            return redirect('order_screen')

    return render(request, "main/order_screen.html")