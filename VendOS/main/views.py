from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product

# Create your views here.
def splash_screen_view(request):
    return render(request, "main/splash_screen.html")

def order_screen_view(request):
    return render(request, "main/order_screen.html")

def order_package(request):
    if request.method == "POST":
        slot_code = request.POST.get("slot_code")
        try:
            product = Product.objects.get(slot_id=slot_code)
            if product.stock > 0:
                # do not alter the product stock yet, wait for payment confirmation
                return redirect('checkout', product_slot=slot_code) 
            else:
                # Out of stock
                messages.error(request, "The selected slot is out of stock.")
                return render(request, "main/order_screen.html", {"error": "Out of stock"})
        except Product.DoesNotExist:
            # Invalid slot
            messages.error(request, "The slot code you selected does not exist. Please try again.")
            return render(request, "main/order_screen.html", {"error": "Invalid slot"})
    return render(request, "main/order_screen.html")