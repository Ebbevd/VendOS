from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product
import requests

# Create your views here.
def splash_screen_view(request):
    return render(request, "main/splash_screen.html")

def order_screen_view(request):
    # Check ngrok first 
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        for t in tunnels["tunnels"]:
            if t["proto"] == "https":
                context = {
                    "time_out": 300,  # seconds before redirecting to splash screen
                }
                return render(request, "main/order_screen.html", context)
    except Exception as e:
        print("Could not get ngrok URL:", e)
        print("Redirecting to error page")
        return render(request, "payments/error_page.html")

    
    
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